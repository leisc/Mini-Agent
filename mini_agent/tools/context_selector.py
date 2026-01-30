"""Context selection utilities for LLM calls.

This module provides a lightweight `ContextSelector` class that scores
and selects the most relevant pieces of context (messages, documents,
tool outputs) to include in an LLM prompt while respecting a token
budget. The implementation uses simple, dependency-free heuristics so
it can be used as a prototype in the agent.

Usage:
    selector = ContextSelector()
    selected = selector.select_context(
        query="summarize recent changes",
        documents=[{"source": "notes", "text": "...", "ts": 1690000000}],
        messages=["User: ...", "Assistant: ..."],
        token_budget=1500,
    )
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import math
import time


@dataclass
class ContextItem:
    source: str
    text: str
    metadata: Dict[str, Any]
    score: float = 0.0


class ContextSelector:
    """Selects and truncates context pieces to fit a target token budget.

    This selector implements a simple heuristic ranking based on:
    - lexical overlap with the `query` (higher weight)
    - recency (if a `ts` timestamp is provided in metadata)
    - an optional importance weight in metadata (e.g. metadata['w'])

    The selector then includes highest-scoring items until the estimated
    token budget is reached. Token estimation is conservative and counts
    words as approximate tokens.
    """

    def __init__(self, avg_tokens_per_word: float = 1.0):
        self.avg_tokens_per_word = avg_tokens_per_word

    def _estimate_tokens(self, text: str) -> int:
        # conservative word-based estimation (fast, no external deps)
        words = text.split()
        return max(1, int(len(words) * self.avg_tokens_per_word))

    def _lexical_score(self, query: str, text: str) -> float:
        q_words = set(w.lower() for w in query.split())
        t_words = set(w.lower() for w in text.split())
        if not q_words or not t_words:
            return 0.0
        overlap = q_words & t_words
        return len(overlap) / max(1, len(q_words))

    def _recency_score(self, metadata: Dict[str, Any]) -> float:
        ts = metadata.get("ts")
        if not ts:
            return 0.0
        # newer items get scores in (0,1]; very old items approach 0
        age = max(0.0, time.time() - float(ts))
        # use a soft decay (seconds -> days scale)
        days = age / (60 * 60 * 24)
        return 1.0 / (1.0 + days)

    def _importance_score(self, metadata: Dict[str, Any]) -> float:
        w = metadata.get("w")
        try:
            return float(w)
        except Exception:
            return 0.0

    def score_item(self, item: ContextItem, query: str) -> float:
        lex = self._lexical_score(query, item.text)
        rec = self._recency_score(item.metadata)
        imp = self._importance_score(item.metadata)
        # combine with weights: lexical most important
        score = 0.7 * lex + 0.2 * rec + 0.1 * imp
        return float(score)

    def select_context(
        self,
        query: str,
        documents: Optional[List[Union[str, Dict[str, Any]]]] = None,
        messages: Optional[List[Union[str, Dict[str, Any]]]] = None,
        tools_outputs: Optional[List[Union[str, Dict[str, Any]]]] = None,
        token_budget: int = 1500,
    ) -> List[Dict[str, Any]]:
        """Return a list of selected context items (dicts).

        Each returned item contains: `source`, `text`, `metadata`, `score`,
        and `est_tokens`.
        """
        documents = documents or []
        messages = messages or []
        tools_outputs = tools_outputs or []

        items: List[ContextItem] = []

        def normalize(src: str, entry: Union[str, Dict[str, Any]]):
            if isinstance(entry, str):
                return ContextItem(source=src, text=entry, metadata={})
            if isinstance(entry, dict):
                text = entry.get("text") or entry.get("content") or ""
                meta = {k: v for k, v in entry.items() if k != "text" and k != "content"}
                return ContextItem(source=src, text=str(text), metadata=meta)
            return ContextItem(source=src, text=str(entry), metadata={})

        for d in documents:
            items.append(normalize("document", d))
        for m in messages:
            items.append(normalize("message", m))
        for t in tools_outputs:
            items.append(normalize("tool", t))

        for it in items:
            it.score = self.score_item(it, query)

        # sort by descending score, break ties by shorter estimated tokens
        items.sort(key=lambda x: (x.score, -len(x.text)), reverse=True)

        selected = []
        used_tokens = 0

        for it in items:
            est = self._estimate_tokens(it.text)
            if used_tokens + est > token_budget:
                # try to include a truncated version if item is highly relevant
                if it.score >= 0.6 and used_tokens < token_budget:
                    remaining = token_budget - used_tokens
                    # naive truncation by words
                    words = it.text.split()
                    truncated = " ".join(words[: max(1, int(remaining / max(1, self.avg_tokens_per_word)))])
                    sel_text = truncated
                    sel_est = self._estimate_tokens(sel_text)
                    selected.append({
                        "source": it.source,
                        "text": sel_text,
                        "metadata": it.metadata,
                        "score": it.score,
                        "est_tokens": sel_est,
                    })
                    used_tokens += sel_est
                continue
            selected.append({
                "source": it.source,
                "text": it.text,
                "metadata": it.metadata,
                "score": it.score,
                "est_tokens": est,
            })
            used_tokens += est
            if used_tokens >= token_budget:
                break

        return selected
