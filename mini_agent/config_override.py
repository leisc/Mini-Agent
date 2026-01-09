"""Configuration runtime override system.

Provides flexible configuration overriding through:
- Environment variables with MINI_AGENT_ prefix
- CLI arguments
- Optional override file (config-override.yaml)

Priority order: CLI > Environment > Override File > Base Config
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class OverrideSource:
    """Metadata about where a configuration value comes from"""
    value: Any
    source: str  # "yaml", "override_yaml", "env", "cli", "default"

    def __str__(self) -> str:
        return f"{self.value} (from {self.source})"


class ConfigOverride:
    """Configuration override management system"""

    # Mapping of environment variables to config paths
    ENV_VAR_MAPPING = {
        # LLM Configuration
        "MINI_AGENT_API_KEY": ("llm", "api_key"),
        "MINI_AGENT_API_BASE": ("llm", "api_base"),
        "MINI_AGENT_MODEL": ("llm", "model"),
        "MINI_AGENT_PROVIDER": ("llm", "provider"),
        "MINI_AGENT_PROXY": ("llm", "proxy"),
        "MINI_AGENT_REASONING_SPLIT": ("llm", "reasoning_split"),
        "MINI_AGENT_RETRY_ENABLED": ("llm", "retry", "enabled"),
        "MINI_AGENT_MAX_RETRIES": ("llm", "retry", "max_retries"),
        "MINI_AGENT_INITIAL_DELAY": ("llm", "retry", "initial_delay"),
        "MINI_AGENT_MAX_DELAY": ("llm", "retry", "max_delay"),
        "MINI_AGENT_EXPONENTIAL_BASE": ("llm", "retry", "exponential_base"),

        # Agent Configuration
        "MINI_AGENT_MAX_STEPS": ("agent", "max_steps"),
        "MINI_AGENT_WORKSPACE_DIR": ("agent", "workspace_dir"),
        "MINI_AGENT_SYSTEM_PROMPT_PATH": ("agent", "system_prompt_path"),

        # Tools Configuration
        "MINI_AGENT_ENABLE_FILE_TOOLS": ("tools", "enable_file_tools"),
        "MINI_AGENT_ENABLE_BASH": ("tools", "enable_bash"),
        "MINI_AGENT_ENABLE_NOTE": ("tools", "enable_note"),
        "MINI_AGENT_ENABLE_SKILLS": ("tools", "enable_skills"),
        "MINI_AGENT_SKILLS_DIR": ("tools", "skills_dir"),
        "MINI_AGENT_ENABLE_MCP": ("tools", "enable_mcp"),
        "MINI_AGENT_MCP_CONFIG_PATH": ("tools", "mcp_config_path"),
    }

    # Type conversion functions for different fields
    TYPE_CONVERTERS = {
        bool: lambda x: str(x).lower() in ("true", "1", "yes", "on"),
        int: lambda x: int(x),
        float: lambda x: float(x),
        str: lambda x: str(x),
    }

    def __init__(self, verbose: bool = False):
        """
        Initialize override system.

        Args:
            verbose: Print override information
        """
        self.verbose = verbose
        self.overrides: Dict[str, OverrideSource] = {}
        self.cli_args: Dict[str, Any] = {}

    def set_cli_override(self, path: str, value: Any):
        """
        Set a CLI override.

        Args:
            path: Dot-separated config path (e.g., "llm.model")
            value: Override value
        """
        self.cli_args[path] = value

    def get_env_overrides(self) -> Dict[str, Any]:
        """Get all environment variable overrides."""
        overrides = {}

        for env_var, path_tuple in self.ENV_VAR_MAPPING.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate through nested structure
                current = overrides
                for part in path_tuple[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Convert value type
                field_name = path_tuple[-1]
                converted_value = self._convert_value(value, field_name)
                current[field_name] = converted_value

                if self.verbose:
                    self.overrides[f"{'.'.join(path_tuple)}"] = OverrideSource(
                        converted_value, "env"
                    )

        return overrides

    def get_file_overrides(self, override_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get overrides from config-override.yaml file.

        Args:
            override_path: Optional override file path. If None, searches standard locations.
        """
        import yaml

        if override_path is None:
            # Search for override file in standard locations
            from .config import Config
            override_path = Config.find_config_file("config-override.yaml")

        if override_path is None or not override_path.exists():
            if self.verbose:
                print(f"No override file found at {override_path}")
            return {}

        with open(override_path, encoding="utf-8") as f:
            override_data = yaml.safe_load(f) or {}

        if self.verbose and override_data:
            print(f"Loaded overrides from: {override_path}")

        return override_data

    def apply_overrides(self, config_dict: Dict[str, Any], override_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Apply all overrides to configuration dict.

        Priority: CLI > Environment > Override File > Base Config

        Args:
            config_dict: Base configuration dictionary
            override_file: Optional path to override file

        Returns:
            Merged configuration dictionary
        """
        import copy

        result = copy.deepcopy(config_dict)

        # Apply file overrides
        file_overrides = self.get_file_overrides(override_file)
        if file_overrides:
            result = self._deep_merge(result, file_overrides)
            if self.verbose:
                for key, value in file_overrides.items():
                    self._track_overrides(result, [key], "override_yaml", value)

        # Apply environment overrides
        env_overrides = self.get_env_overrides()
        if env_overrides:
            result = self._deep_merge(result, env_overrides)

        # Apply CLI overrides
        if self.cli_args:
            for path, value in self.cli_args.items():
                path_parts = path.split(".")
                self._set_nested_value(result, path_parts, value)
                self.overrides[path] = OverrideSource(value, "cli")

        # Print summary if verbose
        if self.verbose and self.overrides:
            print(f"\n{'=' * 60}")
            print("Configuration Override Summary:")
            print(f"{'=' * 60}")
            for key, source in sorted(self.overrides.items()):
                print(f"  {key:30s} -> {source}")
            print(f"{'=' * 60}\n")

        return result

    def _convert_value(self, value: str, field_name: str) -> Any:
        """Convert string value to appropriate type based on field name."""
        # Boolean fields
        if field_name in ("enabled", "enable_file_tools", "enable_bash", "enable_note",
                         "enable_skills", "enable_mcp", "reasoning_split"):
            return self.TYPE_CONVERTERS[bool](value)

        # Numeric fields
        if field_name in ("max_steps", "initial_delay", "max_delay", "exponential_base",
                         "max_retries"):
            if "." in value:
                return self.TYPE_CONVERTERS[float](value)
            return self.TYPE_CONVERTERS[int](value)

        # String fields (default)
        return self.TYPE_CONVERTERS[str](value)

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        import copy

        result = copy.deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _set_nested_value(self, data: Dict, path_parts: list, value: Any):
        """Set a value in nested dictionary using path parts."""
        current = data
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[path_parts[-1]] = value

    def _track_overrides(self, data: Dict, path: list, source: str, value: Any):
        """Track override sources recursively."""
        if isinstance(value, dict):
            for k, v in value.items():
                self._track_overrides(data, path + [k], source, v)
        else:
            self.overrides[".".join(path)] = OverrideSource(value, source)


def load_config_with_overrides(
    override_file: Optional[Path] = None,
    cli_args: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> "Config":
    """
    Load configuration with overrides applied.

    This is the main entry point for loading configuration with runtime overrides.

    Args:
        override_file: Optional path to override file
        cli_args: Optional CLI arguments as dict {path: value}
        verbose: Print override information

    Returns:
        Config instance with overrides applied

    Example:
        config = load_config_with_overrides(
            cli_args={"llm.model": "gpt-4"},
            verbose=True
        )
    """
    from .config import Config

    # Create override manager
    override_manager = ConfigOverride(verbose=verbose)

    # Apply CLI args if provided
    if cli_args:
        for path, value in cli_args.items():
            override_manager.set_cli_override(path, value)

    # Load base config as dict
    base_config = Config.load().model_dump()

    # Apply overrides
    merged_config = override_manager.apply_overrides(base_config, override_file=override_file)

    # Reconstruct Config object
    return Config(**merged_config)