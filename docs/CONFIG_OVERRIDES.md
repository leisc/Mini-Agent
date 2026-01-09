# Configuration Override System

## Overview

Mini-Agent now supports flexible runtime configuration overrides through multiple mechanisms with clear priority ordering.

## Priority Chain

```
CLI Arguments (highest)
    ↓
Environment Variables
    ↓
Override File (config-override.yaml)
    ↓
Base Config (config.yaml)
```

---

## Usage Methods

### 1. Environment Variables (Recommended)

Set environment variables with the `MINI_AGENT_` prefix:

```bash
# LLM Configuration
export MINI_AGENT_API_KEY="your-api-key"
export MINI_AGENT_MODEL="gpt-4"
export MINI_AGENT_API_BASE="https://api.openai.com"
export MINI_AGENT_PROVIDER="openai"

# Agent Configuration
export MINI_AGENT_MAX_STEPS=200
export MINI_AGENT_WORKSPACE_DIR="./my-workspace"

# Tools Configuration
export MINI_AGENT_ENABLE_SKILLS=true
export MINI_AGENT_ENABLE_MCP=false

# Retry Configuration
export MINI_AGENT_MAX_RETRIES=5
export MINI_AGENT_RETRY_ENABLED=true
```

Then run normally:
```bash
mini-agent
```

### 2. CLI Arguments

Override configuration directly from command line:

```bash
# Single override
mini-agent --config-override llm.model=gpt-4

# Multiple overrides
mini-agent \
  --config-override llm.model=gpt-4 \
  --config-override agent.max_steps=200 \
  --config-override tools.enable_mcp=false

# Complex values (JSON)
mini-agent --config-override 'llm.retry={"enabled":true,"max_retries":5}'
```

### 3. Override File

Create a `config-override.yaml` file:

```yaml
llm:
  model: "gpt-4"
  provider: "openai"
  retry:
    max_retries: 5
    initial_delay: 2.0

agent:
  max_steps: 200
  workspace_dir: "./dev-workspace"

tools:
  enable_mcp: false
```

Run with override file:
```bash
mini-agent --override-file config-override.yaml
# or just place it in config directory
mini-agent
```

### 4. Programmatic (Python Code)

```python
from mini_agent.config import Config

# Load withoverrides
config = Config.load_with_overrides(
    cli_args={
        "llm.model": "gpt-4",
        "agent.max_steps": 200,
    },
    verbose=True
)

print(config.llm.model)  # "gpt-4"
print(config.agent.max_steps)  # 200
```

---

## Available Override Variables

### LLM Configuration

| Environment Variable | Config Path | Expected Type | Default |
|---------------------|-------------|---------------|---------|
| `MINI_AGENT_API_KEY` | `llm.api_key` | string | Required |
| `MINI_AGENT_API_BASE` | `llm.api_base` | string | https://api.minimax.io |
| `MINI_AGENT_MODEL` | `llm.model` | string | MiniMax-M2 |
| `MINI_AGENT_PROVIDER` | `llm.provider` | string | anthropic |
| `MINI_AGENT_PROXY` | `llm.proxy` | string | null |
| `MINI_AGENT_REASONING_SPLIT` | `llm.reasoning_split` | boolean | false |

### Retry Configuration

| Environment Variable | Config Path | Expected Type | Default |
|---------------------|-------------|---------------|---------|
| `MINI_AGENT_RETRY_ENABLED` | `llm.retry.enabled` | boolean | true |
| `MINI_AGENT_MAX_RETRIES` | `llm.retry.max_retries` | integer | 3 |
| `MINI_AGENT_INITIAL_DELAY` | `llm.retry.initial_delay` | float | 1.0 |
| `MINI_AGENT_MAX_DELAY` | `llm.retry.max_delay` | float | 60.0 |
| `MINI_AGENT_EXPONENTIAL_BASE` | `llm.retry.exponential_base` | float | 2.0 |

### Agent Configuration

| Environment Variable | Config Path | Expected Type | Default |
|---------------------|-------------|---------------|---------|
| `MINI_AGENT_MAX_STEPS` | `agent.max_steps` | integer | 50 |
| `MINI_AGENT_WORKSPACE_DIR` | `agent.workspace_dir` | string | ./workspace |
| `MINI_AGENT_SYSTEM_PROMPT_PATH` | `agent.system_prompt_path` | string | system_prompt.md |

### Tools Configuration

| Environment Variable | Config Path | Expected Type | Default |
|---------------------|-------------|---------------|---------|
| `MINI_AGENT_ENABLE_FILE_TOOLS` | `tools.enable_file_tools` | boolean | true |
| `MINI_AGENT_ENABLE_BASH` | `tools.enable_bash` | boolean | true |
| `MINI_AGENT_ENABLE_NOTE` | `tools.enable_note` | boolean | true |
| `MINI_AGENT_ENABLE_SKILLS` | `tools.enable_skills` | boolean | true |
| `MINI_AGENT_SKILLS_DIR` | `tools.skills_dir` | string | ./skills |
| `MINI_AGENT_ENABLE_MCP` | `tools.enable_mcp` | boolean | true |
| `MINI_AGENT_MCP_CONFIG_PATH` | `tools.mcp_config_path` | string | mcp.json |

---

## Advanced Features

### Verbose Override Information

See what's being overridden and from where:

```bash
# Show override summary
mini-agent --config-override llm.model=gpt-4 --config-verbose
```

Output:
```
============================================================
Configuration Override Summary:
============================================================
  llm.model                      -> gpt-4 (from cli)
============================================================
```

### Disable Environment Overrides

Temporarily disable all environment variable overrides:

```bash
# Environment vars will be ignored
mini-agent --no-env-overrides
```

### Override File Locations

Override files are searched in priority order:
1. `./mini_agent/config/config-override.yaml` (development)
2. `~/.mini-agent/config/config-override.yaml` (user)
3. `<package>/mini_agent/config/config-override.yaml` (installed)

---

## Examples

### Example 1: Development Setup

Use different configs for dev/staging/prod:

```bash
# Development
export MINI_AGENT_MODEL="gpt-3.5-turbo"
export MINI_AGENT_MAX_STEPS=50
mini-agent

# Staging
export MINI_AGENT_MODEL="gpt-4"
export MINI_AGENT_MAX_STEPS=200
export MINI_AGENT_API_BASE="https://staging-api.example.com"
mini-agent

# Production
export MINI_AGENT_MODEL="gpt-4-turbo"
export MINI_AGENT_MAX_RETRIES=5
export MINI_AGENT_RETRY_ENABLED=true
export MINI_AGENT_API_BASE="https://api.example.com"
mini-agent
```

### Example 2: CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: pip install -e .

      - name: Run tests with config overrides
        env:
          MINI_AGENT_API_KEY: ${{ secrets.TEST_API_KEY }}
          MINI_AGENT_MODEL: "gpt-3.5-turbo"
          MINI_AGENT_MAX_STEPS: 10
          MINI_AGENT_ENABLE_MCP: false
        run: pytest tests/
```

### Example 3: Multiple Environments

Create environment-specific override files:

```bash
# dev-override.yaml
llm:
  model: "gpt-3.5-turbo"

# prod-override.yaml
llm:
  model: "gpt-4"
  retry:
    max_retries: 5

# Use specific environment
mini-agent --override-file prod-override.yaml
```

### Example 4: Programmatic Configuration

```python
#!/usr/bin/env python
import asyncio
from mini_agent import LLMClient, Agent
from mini_agent.config import Config

async def main():
    # Load config with custom overrides
    config = Config.load_with_overrides(
        cli_args={
            "llm.model": "gpt-4",
            "agent.max_steps": 300,
            "llm.retry.max_retries": 5,
        },
        verbose=True
    )

    # Initialize agent with overridden config
    llm = LLMClient(
        api_key=config.llm.api_key,
        api_base=config.llm.api_base,
        model=config.llm.model,
    )

    agent = Agent(
        llm_client=llm,
        system_prompt="You are a helpful assistant",
        tools=[],  # Your tools here
        max_steps=config.agent.max_steps,
    )

    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

### 1. Security
- Never commit API keys to version control
- Use environment variables for sensitive values
- Use separate override files per environment

### 2. Team Collaboration
- Document your environment variables in `.env.example`
- Use override files for environment-specific settings
- Keep base config (`config.yaml`) with sensible defaults

### 3. Debugging
- Use `--config-verbose` to see active overrides
- Check which source is being used for each value
- Use `--no-env-overrides` to isolate config file issues

### 4. Production
- Set all production values via environment variables
- Use strict validation in CI/CD
- Monitor configuration changes

---

## Configuration Migration Guide

### Before (single config.yaml)
```yaml
api_key: "sk-xxx"
model: "gpt-4"
max_steps: 100
```

### After (with overrides)
```yaml
# config.yaml (base, committed to git)
api_key: "YOUR_API_KEY_HERE"  # Placeholder
model: "MiniMax-M2"  # Default model
max_steps: 50

# .env (not committed to git)
MINI_AGENT_API_KEY="sk-xxx"
MINI_AGENT_MODEL="gpt-4"
MINI_AGENT_MAX_STEPS=100
```

Run with:
```bash
source .env
mini-agent
```

---

## Troubleshooting

### Override not working?

1. Check with --config-verbose to see what's applied
2. Check environment variable names (must use MINI_AGENT_ prefix)
3. Check CLI argument format (must be "key=value")

### Need to see all valid env vars?

```python
from mini_agent.config_override import ConfigOverride

manager = ConfigOverride()
for env_var, path in manager.ENV_VAR_MAPPING.items():
    print(f"{env_var} -> {'.'.join(path)}")
```

### Want to disable all overrides?

```bash
cli:
mini-agent --no-env-overrides
# Without override file
```

---

## Migration from Old Config

The override system is **100% backward compatible**. Your existing `config.yaml` will work exactly as before. Overrides are optional.

To start using overrides:
1. Keep your existing `config.yaml`
2. Optionally create `config-override.yaml` for environment-specific values
3. Set environment variables for secrets
4. Use CLI args for quick experiments

---

## API Reference

### Config.load_with_overrides()

Load configuration with overrides applied.

```python
def load_with_overrides(
    override_file: Optional[Path] = None,
    cli_args: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
    env_overrides: bool = True,
) -> Config:
    """..."""
```

**Parameters:**
- `override_file`: Path to override YAML file
- `cli_args`: Dictionary of CLI-style overrides {"path": value}
- `verbose`: Print override information
- `env_overrides`: Enable environment variable overrides

**Returns:** Config instance with overrides applied