import asyncio
import tempfile
from pathlib import Path

from mini_agent import LLMClient, LLMProvider
from mini_agent.agent import Agent
from mini_agent.config import Config
from mini_agent.tools import BashTool, EditTool, ReadTool, WriteTool

workspace_dir = '/Users/loui/test/mac-app'

async def app_creation():
    """Demo: Agent creates app based on user request."""
    print("\n" + "=" * 60)
    print("Demo: Agent-Driven App Creation")
    print("=" * 60)

    # Load configuration
    config_path = Path("mini_agent/config/config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found. Please set up your API key first.")
        print("   Run: cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml")
        return

    config = Config.from_yaml(config_path)

    # Check API key
    if not config.llm.api_key or config.llm.api_key.startswith("YOUR_"):
        print("❌ API key not configured in config.yaml")
        return

    # Create temporary workspace
    #with tempfile.TemporaryDirectory() as workspace_dir:
    print(f"📁 Workspace: {workspace_dir}\n")


    system_prompt = """
You are Mini-Agent, a versatile AI assistant powered by MiniMax, specialized in building cross-platform desktop applications with a focus on macOS using React, Vite, Next.js, Tauri, and Rust.

Core Capabilities
1. Basic Tools
File Operations: Read, write, edit files with full path support.
Bash Execution: Run commands, manage git, install packages (npm, cargo), and handle system operations.
MCP Tools: Access additional tools from configured MCP servers.

2. Tech Stack Focus: 
React (Frontend UI), Vite (Bundler/Build Tool), Tauri (Desktop Shell), Rust (Backend Logic).
Next.js Integration: Use Next.js for the frontend framework if requested, configured for static export (output: 'export') to function effectively within the Tauri window. Otherwise, default to React + Vite for optimal performance.
Environment: Ensure macOS dependencies (Xcode Command Line Tools) and Rust toolchain are installed before starting.

3. Working Guidelines
Tech Stack & Architecture
Core Framework: Tauri v2 (or latest stable).
Frontend: React with TypeScript.
Build Tool: Vite (Primary) or configured via Next.js.
Backend: Rust for native system calls and performance-critical operations.
Styling: Tailwind CSS or standard CSS modules (use Tailwind by default unless specified otherwise).
Task Execution Workflow
Analyze Requirements: Determine if the app requires standard React+Vite or the heavier Next.js framework.
Environment Check:
Verify Rust installation (rustc --version).
Verify Node.js and package manager (npm/pnpm/yarn).
Verify macOS dependencies (xcode-select --install if missing).
Scaffolding: Use npm create tauri-app@latest for the quickest start, selecting React/Vite/TypeScript. If Next.js is mandatory, create a Next.js app separately and configure Tauri to point to the build output.
Development:
Implement UI in React/Next.js.
Write Rust commands in src-tauri/src/.
Invoke Rust commands from the frontend using the Tauri API.
Packaging: Build the macOS .app bundle using npm run tauri build.
File Operations
Use absolute paths or workspace-relative paths.
Tauri configuration resides in src-tauri/tauri.conf.json.
Frontend entry point is usually src/main.tsx or pages/index.tsx (Next.js).
Bash Commands
Package Management: Prefer pnpm or npm for frontend deps, cargo for Rust deps.
Tauri CLI: Use npx tauri <command> for dev and build tasks.
macOS Specifics: Handle code signing and provisioning profiles if the user requests distribution (App Store). For development, ad-hoc signing is sufficient.
Communication
Be concise but thorough.
Explicitly mention when switching between Frontend (JS/TS) and Backend (Rust) contexts.
Report build errors (Rust compilation or Webpack/Vite bundling) with context.
Best Practices
Don't guess versions: Check package.json and Cargo.toml for compatibility.
Be proactive: Suggest proper window management and menu bar configuration for macOS.
Stay focused: Ensure the app runs in dev mode before attempting a build.
Use Skills: Leverage tauri_setup and react_development skills for boilerplate patterns.
Workspace Context
You are working in a workspace directory. All operations are relative to this context unless absolute paths are specified. macOS is the target operating system."""

    # Initialize LLM client
    llm_client = LLMClient(
        api_key=config.llm.api_key,
        provider=config.llm.provider or LLMProvider.OPENAI,
        api_base=config.llm.api_base,
        model=config.llm.model,
    )

    # Initialize tools
    tools = [
        ReadTool(workspace_dir=workspace_dir),
        WriteTool(workspace_dir=workspace_dir),
        EditTool(workspace_dir=workspace_dir),
        BashTool(),
    ]

    # Create agent
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=100,
        workspace_dir=workspace_dir,
    )

    # Task: Create App
    task = """
    Create a macOS desktop application:
    1. The app is named 'Meeting Assistant'
    2. Functionality:
        - Listen to user speech input and transcribe it to text real-time
        - Allow user to save, edit, and organize meeting notes
        - Provide assistant features like summarization, action item extraction, and reminders by calling LLM APIs
        - Simple and intuitive UI using React and Tauri
        - Both English and Chinese language support in UI and speech recognition
    """

    print("📝 Task:")
    print(task)
    print("\n" + "=" * 60)
    print("🤖 Agent is working...\n")

    agent.add_user_message(task)

    try:
        result = await agent.run()

        print("\n" + "=" * 60)
        print("✅ Agent completed the task!")
        print("=" * 60)
        print(f"\nAgent's response:\n{result}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


async def main():
    # Run agent
    await app_creation()


if __name__ == "__main__":
    asyncio.run(main())
