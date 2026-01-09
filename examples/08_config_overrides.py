"""
Configuration Override Examples

Demonstrates various ways to use the runtime override system.
"""

import asyncio
from pathlib import Path
from mini_agent import LLMClient, Agent
from mini_agent.config import Config
from mini_agent.tools import ReadTool, WriteTool, BashTool


def example_1_basic_overrides():
    """Example 1: Basic CLI-style overrides."""
    print("=" * 60)
    print("Example 1: Basic CLI-style overrides")
    print("=" * 60)

    config = Config.load_with_overrides(
        cli_args={
            "llm.model": "gpt-4",
            "agent.max_steps": 200,
            "tools.enable_mcp": False,
        },
        verbose=True,
    )

    print(f"\nModel: {config.llm.model}")
    print(f"Max steps: {config.agent.max_steps}")
    print(f"MCP enabled: {config.tools.enable_mcp}")


def example_2_override_file():
    """Example 2: Load config with override file."""
    print("\n" + "=" * 60)
    print("Example 2: Override file")
    print("=" * 60)

    # Create example override file
    override_content = """
llm:
  model: "gpt-4-turbo"
  retry:
    max_retries: 5

agent:
  max_steps: 300
  workspace_dir: "./test-workspace"
"""
    override_path = Path("test-override.yaml")
    override_path.write_text(override_content)

    try:
        config = Config.load_with_overrides(
            override_file=override_path,
            verbose=True,
        )

        print(f"\nModel: {config.llm.model}")
        print(f"Max retries: {config.llm.retry.max_retries}")
        print(f"Max steps: {config.agent.max_steps}")
    finally:
        override_path.unlink()


def example_3_env_simulation():
    """Example 3: Simulate environment variable overrides."""
    print("\n" + "=" * 60)
    print("Example 3: Environment variable overrides")
    print("=" * 60)

    import os
    from mini_agent.config_override import ConfigOverride

    # Set environment variables
    os.environ["MINI_AGENT_MODEL"] = "gpt-3.5-turbo"
    os.environ["MINI_AGENT_MAX_STEPS"] = "150"
    os.environ["MINI_AGENT_MAX_RETRIES"] = "10"

    try:
        config = Config.load_with_overrides(verbose=True)

        print(f"\nModel: {config.llm.model}")
        print(f"Max steps: {config.agent.max_steps}")
        print(f"Max retries: {config.llm.retry.max_retries}")
    finally:
        # Cleanup
        del os.environ["MINI_AGENT_MODEL"]
        del os.environ["MAX_STEPS"]
        del os.environ["MAX_RETRIES"]


def example_4_combined():
    """Example 4: Combined overrides (all sources)."""
    print("\n" + "=" * 60)
    print("Example 4: Combined overrides")
    print("=" * 60)

    # Override file with some values
    override_content = """
llm:
  retry:
    enabled: true

tools:
  enable_skills: false
"""
    override_path = Path("test-combined-override.yaml")
    override_path.write_text(override_content)

    # Environment variables
    import os
    os.environ["MINI_AGENT_MAX_STEPS"] = "250"

    # CLI args
    cli_args = {
        "llm.model": "gpt-4-turbo",
        "agent.workspace_dir": "./combined-workspace",
    }

    try:
        config = Config.load_with_overrides(
            override_file=override_path,
            cli_args=cli_args,
            verbose=True,
        )

        print(f"\nModel: {config.llm.model}")  # From CLI
        print(f"Max steps: {config.agent.max_steps}")  # From env
        print(f"Retry enabled: {config.llm.retry.enabled}")  # From file
        print(f"Skills enabled: {config.tools.enable_skills}")  # From file
        print(f"Workspace: {config.agent.workspace_dir}")  # From CLI

    finally:
        override_path.unlink()
        del os.environ["MINI_AGENT_MAX_STEPS"]


async def example_5_practical_use():
    """Example 5: Practical use with Agent."""
    print("\n" + "=" * 60)
    print("Example 5: Practical Agent usage with overrides")
    print("=" * 60)

    # Load config with overrides
    config = Config.load_with_overrides(
        cli_args={
            "llm.model": "gpt-3.5-turbo",  # Use cheaper model for testing
            "agent.max_steps": 10,  # Limit steps for quick test
            "tools.enable_mcp": False,  # Disable MCP for testing
        },
        verbose=True,
    )

    # Create temporary workspace
    import tempfile
    with tempfile.TemporaryDirectory() as workspace:
        print(f"\nUsing workspace: {workspace}")

        # Initialize LLM client
        llm = LLMClient(
            api_key=config.llm.api_key,
            api_base=config.llm.api_base,
            model=config.llm.model,
        )

        # Initialize tools
        tools = [
            ReadTool(workspace_dir=workspace),
            WriteTool(workspace_dir=workspace),
            BashTool(),
        ]

        # Create agent
        agent = Agent(
            llm_client=llm,
            system_prompt="You are a helpful assistant.",
            tools=tools,
            max_steps=config.agent.max_steps,
            workspace_dir=workspace,
        )

        print("\n✅ Agent created with overridden configuration!")
        print(f"   - Model: {config.llm.model}")
        print(f"   - Max steps: {config.agent.max_steps}")
        print(f"   - Tools: {len(tools)}")

        # Note: Not actually running to avoid API calls
        # result = await agent.run("Create a test file")


def example_6_priority_demonstration():
    """Example 6: Demonstrate override priority."""
    print("\n" + "=" * 60)
    print("Example 6: Override priority demonstration")
    print("=" * 60)

    # Base config sets Model: "MiniMax-M2"
    # Override file sets Model: "gpt-4"
    # Environment sets Model: "gpt-3.5-turbo"
    # CLI sets Model: "gpt-4-turbo"

    override_content = """
llm:
  model: "gpt-4"
"""
    override_path = Path("test-priority-override.yaml")
    override_path.write_text(override_content)

    import os
    os.environ["MINI_AGENT_MODEL"] = "gpt-3.5-turbo"

    try:
        config = Config.load_with_overrides(
            override_file=override_path,
            cli_args={"llm.model": "gpt-4-turbo"},  # This wins!
            verbose=True,
        )

        print(f"\nFinal model: {config.llm.model}")
        print("\nPriority chain:")
        print("  1. Base config: MiniMax-M2")
        print("  2. Override file: gpt-4")
        print("  3. Environment: gpt-3.5-turbo")
        print("  4. CLI (WINNER): gpt-4-turbo")

    finally:
        override_path.unlink()
        del os.environ["MINI_AGENT_MODEL"]


def main():
    """Run all examples."""
    print("\n" + "🎯 " * 15 + "\n")
    print("Configuration Override System Examples")
    print("\n" + "🎯 " * 15 + "\n")

    # Run synchronous examples
    example_1_basic_overrides()
    example_2_override_file()
    example_3_env_simulation()
    example_4_combined()

    # Run priority demonstration
    example_6_priority_demonstration()

    # Run async example
    asyncio.run(example_5_practical_use())

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()