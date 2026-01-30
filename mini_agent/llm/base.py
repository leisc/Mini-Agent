"""Base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import Any, List

import logging
import json

import tiktoken

from ..retry import RetryConfig
from ..schema import LLMResponse, Message
from ..tools.file_tools import truncate_text_by_tokens

logger = logging.getLogger(__name__)


class LLMClientBase(ABC):
    """Abstract base class for LLM clients.

    This class defines the interface that all LLM clients must implement,
    regardless of the underlying API protocol (Anthropic, OpenAI, etc.).
    """

    def __init__(
        self,
        api_key: str,
        api_base: str,
        model: str,
        proxy: str | None = None,
        reasoning_split: bool = False,
        retry_config: RetryConfig | None = None,
        model_context_limit: int | None = None,
        context_safety_margin: int = 512,
    ):
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication
            api_base: Base URL for the API
            model: Model name to use
            retry_config: Optional retry configuration
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.proxy = proxy
        self.reasoning_split = reasoning_split
        self.retry_config = retry_config or RetryConfig()

        # Context configuration (used by enforce_context_limit)
        self.model_context_limit = model_context_limit
        self.context_safety_margin = context_safety_margin

        # Callback for tracking retry count
        self.retry_callback = None

    def _estimate_tokens_for_messages(self, messages: list[Message]) -> int:
        """Estimate token count for a list of Message objects using cl100k_base.

        This is an approximation (for pruning decisions only).
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        total = 0
        for msg in messages:
            parts = [msg.role]
            # content may be string or structured; stringify for token estimation
            if isinstance(msg.content, str):
                parts.append(msg.content)
            else:
                try:
                    parts.append(json.dumps(msg.content, ensure_ascii=False))
                except Exception:
                    parts.append(str(msg.content))

            if msg.thinking:
                parts.append(msg.thinking)

            if msg.tool_calls:
                try:
                    parts.append(json.dumps([tc.dict() for tc in msg.tool_calls], ensure_ascii=False))
                except Exception:
                    parts.append(str(msg.tool_calls))

            chunk = "\n".join(parts)
            total += len(encoding.encode(chunk, disallowed_special=()))
        return total

    def _estimate_tokens_for_message(self, msg: Message) -> int:
        """Estimate tokens for a single Message (helper)."""
        encoding = tiktoken.get_encoding("cl100k_base")
        parts = [msg.role]
        if isinstance(msg.content, str):
            parts.append(msg.content)
        else:
            try:
                parts.append(json.dumps(msg.content, ensure_ascii=False))
            except Exception:
                parts.append(str(msg.content))

        if msg.thinking:
            parts.append(msg.thinking)

        if msg.tool_calls:
            try:
                parts.append(json.dumps([tc.dict() for tc in msg.tool_calls], ensure_ascii=False))
            except Exception:
                parts.append(str(msg.tool_calls))

        chunk = "\n".join(parts)
        return len(encoding.encode(chunk, disallowed_special=()))

    def enforce_context_limit(self, messages: List[Message], *,
                              model_context_limit: int | None = None,
                              safety_margin: int | None = None) -> List[Message]:
        """Ensure the message list fits within a model context window.

        Strategy:
        - Estimate total tokens; if under limit, return as-is.
        - Truncate very long individual message contents using `truncate_text_by_tokens`.
        - If still too large, prune oldest non-system messages until under limit.

        Returns a possibly-modified copy of messages.
        """
        # Default to a large context if not provided (safe upper bound)
        # Resolve defaults from instance if not provided
        limit = model_context_limit or self.model_context_limit or 65536
        # Use provided safety_margin or instance default
        margin = safety_margin if safety_margin is not None else self.context_safety_margin
        # Target is a bit below limit to leave room for completion tokens
        target = max(1024, limit - margin)

        # Work on a shallow copy
        msgs = [m.copy() for m in messages]

        print(msgs[1])

        total = self._estimate_tokens_for_messages(msgs)
        if total <= target:
            return msgs      

        logger.warning("Context token estimate %d > limit %d; compressing messages", total, target)

        # First, try truncating long message contents
        per_message_target = min(8192, max(512, target // 8))
        for m in msgs:
            if isinstance(m.content, str):
                # estimate tokens for this content
                encoding = tiktoken.get_encoding("cl100k_base")
                tok = len(encoding.encode(m.content, disallowed_special=()))
                if tok > per_message_target:
                    # Truncate content in-place
                    m.content = truncate_text_by_tokens(m.content, per_message_target)

        total = self._estimate_tokens_for_messages(msgs)
        if total <= target:
            return msgs

        # If still too big, perform phase-aware pruning and create a brief summary
        system_msgs = [m for m in msgs if m.role == "system"]
        user_msgs = [m for m in msgs if m.role == "user"]
        assistant_msgs = [m for m in msgs if m.role == "assistant"]
        tool_msgs = [m for m in msgs if m.role == "tool"]

        # Keep essentials: all system messages, first user instruction, last user instruction,
        # and recent assistant planning messages (assistant messages that have thinking)
        preserved: list[Message] = []
        preserved.extend(system_msgs)

        # Preserve first user instruction if exists
        if user_msgs:
            preserved.append(user_msgs[0])

        # Preserve recent assistant planning blocks (with thinking), keep up to 3 most recent
        planning_msgs = [m for m in assistant_msgs if m.thinking]
        if planning_msgs:
            preserved.extend(planning_msgs[-3:])

        # Preserve last user instruction (most recent)
        if user_msgs:
            preserved_ids = {id(m) for m in preserved}
            if id(user_msgs[-1]) not in preserved_ids:
                preserved.append(user_msgs[-1])
                preserved_ids.add(id(user_msgs[-1]))

        # Also always preserve the last few messages (most recent 4) to keep immediate context
        recent_msgs = msgs[-4:]
        for m in recent_msgs:
            if id(m) not in preserved_ids:
                preserved.append(m)
                preserved_ids.add(id(m))

        # Build prunable list as msgs excluding preserved (use ids to avoid unhashable Message)
        prunable = [m for m in msgs if id(m) not in preserved_ids]

        removed_accumulator: list[Message] = []

        # Precompute token counts to avoid repeatedly re-tokenizing large content
        token_counts: dict[int, int] = {}
        for m in preserved + prunable:
            token_counts[id(m)] = self._estimate_tokens_for_message(m)

        preserved_tokens = sum(token_counts.get(id(m), 0) for m in preserved)
        prunable_tokens = sum(token_counts.get(id(m), 0) for m in prunable)

        # Remove oldest prunable messages until under target, subtracting token counts
        max_iterations = max(1000, len(prunable) * 2)
        iterations = 0
        while prunable and (preserved_tokens + prunable_tokens) > target:
            if iterations >= max_iterations:
                logger.warning("Reached pruning iteration limit (%d); stopping pruning early", max_iterations)
                break
            removed = prunable.pop(0)
            removed_accumulator.append(removed)
            removed_tokens = token_counts.get(id(removed), self._estimate_tokens_for_message(removed))
            prunable_tokens -= removed_tokens
            logger.info("Pruned message role=%s token_count=%d during context compression", removed.role, removed_tokens)
            iterations += 1

        # Reassemble compressed messages preserving original chronological order
        allowed_ids = preserved_ids.union({id(m) for m in prunable})
        compressed = [m for m in msgs if id(m) in allowed_ids]

        # If we removed anything, insert a concise system notice summarizing removed content
        if removed_accumulator:
            # Create a short summary by concatenating short excerpts from removed messages
            excerpts: list[str] = []
            for rm in removed_accumulator:
                excerpt_text = ""
                if isinstance(rm.content, str):
                    excerpt_text = rm.content.strip()[:400]
                else:
                    try:
                        excerpt_text = json.dumps(rm.content, ensure_ascii=False)[:400]
                    except Exception:
                        excerpt_text = str(rm.content)[:400]
                excerpts.append(f"[{rm.role}] {excerpt_text}")

            summary_text = "\n\n... [Earlier conversation truncated to fit model context window] ...\n\n" + "\n---\n".join(excerpts)

            # Truncate the summary to a safe token size
            summary_text = truncate_text_by_tokens(summary_text, per_message_target)

            notice = Message(role="system", content=f"Conversation summary (truncated):\n{summary_text}")

            # Insert notice after any existing system messages
            insert_index = 0
            if system_msgs:
                # find last system message index in compressed
                for i, m in enumerate(compressed):
                    if m.role == "system":
                        insert_index = i + 1
                compressed.insert(insert_index, notice)
            else:
                compressed.insert(0, notice)

        return compressed

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        tools: list[Any] | None = None,
    ) -> LLMResponse:
        """Generate response from LLM.

        Args:
            messages: List of conversation messages
            tools: Optional list of Tool objects or dicts

        Returns:
            LLMResponse containing the generated content, thinking, and tool calls
        """
        pass

    @abstractmethod
    def _prepare_request(
        self,
        messages: list[Message],
        tools: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Prepare the request payload for the API.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools

        Returns:
            Dictionary containing the request payload
        """
        pass

    @abstractmethod
    def _convert_messages(self, messages: list[Message]) -> tuple[str | None, list[dict[str, Any]]]:
        """Convert internal message format to API-specific format.

        Args:
            messages: List of internal Message objects

        Returns:
            Tuple of (system_message, api_messages)
        """
        pass
