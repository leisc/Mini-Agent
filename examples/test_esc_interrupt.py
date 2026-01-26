"""Test script to demonstrate ESC key interrupt functionality.

This script shows how to use the ESC key to interrupt agent execution.
"""

import asyncio
from mini_agent import Agent, LLMClient
from mini_agent.tools import ReadFile, WriteFile


async def test_esc_interrupt():
    """Test ESC key interrupt during agent execution."""
    print("=" * 60)
    print("ESC Key Interrupt Test")
    print("=" * 60)
    print("\nThis test will run for 50 steps. Press ESC at any time to interrupt.")
    print("The agent will stop gracefully and return an interruption message.\n")

    # Create a simple LLM client (using a mock or placeholder)
    # In a real scenario, you would create a proper LLMClient
    print("Note: Using a mock LLM client for demonstration.")
    print("Press ESC anytime to interrupt the test...\n")

    # Create agent with tools
    agent = Agent(
        llm_client=None,  # Would be a real LLM client in production
        system_prompt="You are a helpful assistant that responds briefly.",
        tools=[ReadFile(), WriteFile()],
        max_steps=50,
        workspace_dir="./test_workspace"
    )

    # Run the agent
    result = await agent.run()

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    asyncio.run(test_esc_interrupt())
