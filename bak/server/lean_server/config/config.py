"""
This module defines the configuration models and loading mechanism for the server.
"""

import argparse
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class LeanConfig(BaseModel):
    """Configuration specific to the Lean environment."""

    executable: str = Field(..., description="The path to the Lean executable.")
    workspace: str = Field(..., description="The path to the Lean workspace.")
    concurrency: int = Field(
        ..., description="The maximum number of concurrent Lean processes."
    )


class SQLiteConfig(BaseModel):
    """Configuration for the SQLite database."""

    database_path: str = Field(
        ..., description="The file path for the SQLite database."
    )
    timeout: int = Field(..., description="The connection timeout in seconds.")


class Config(BaseModel):
    """The main configuration model for the application."""

    host: str = Field(..., description="The host to bind the server to.")
    port: int = Field(..., description="The port to run the server on.")
    lean: LeanConfig = Field(..., description="The Lean-specific configuration.")
    sqlite: SQLiteConfig = Field(..., description="The SQLite-specific configuration.")
    logging: dict[str, Any] = Field(
        ..., description="The logging configuration dictionary."
    )


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deeply merges two dictionaries, with override values taking precedence.

    Args:
        base: The base dictionary.
        override: The dictionary with values to override.

    Returns:
        The merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_config(
    args: argparse.Namespace,
) -> Config:
    """
    Loads the configuration from files and command-line arguments.

    It starts with a default configuration, overrides it with a custom
    config file if provided, and finally applies any command-line arguments.

    Args:
        args: The parsed command-line arguments.

    Returns:
        A validated Config object.
    """
    # Load default configuration
    default_config_path = Path(__file__).parent / "default_config.yaml"
    with open(default_config_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Apply command-line arguments that have direct overrides
    config_data["host"] = args.host
    config_data["port"] = args.port
    config_data["lean"]["concurrency"] = args.concurrency

    # Load and merge custom config file if provided
    if args.config != "default":
        override_path = Path(args.config)
        if override_path.exists():
            with open(override_path, encoding="utf-8") as f:
                override_data = yaml.safe_load(f)
            config_data = _deep_merge(config_data, override_data)

    # Validate the configuration data
    config = Config.model_validate(config_data)

    # Re-apply command-line arguments to ensure they have the highest priority
    config.host = args.host
    config.port = args.port

    # Apply log level from command line
    if args.log_level:
        if "handlers" in config.logging:
            for handler in config.logging["handlers"].values():
                if isinstance(handler, dict):
                    handler["level"] = args.log_level.upper()
        if "loggers" in config.logging:
            for logger in config.logging["loggers"].values():
                if isinstance(logger, dict):
                    logger["level"] = args.log_level.upper()

    # Apply lean workspace from command line
    if args.lean_workspace != "default":
        config.lean.workspace = args.lean_workspace

    return config
