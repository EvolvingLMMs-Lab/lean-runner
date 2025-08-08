import argparse
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class LeanConfig(BaseModel):
    executable: str
    workspace: str
    concurrency: int


class SQLiteConfig(BaseModel):
    database_path: str
    timeout: int


class Config(BaseModel):
    host: str
    port: int
    lean: LeanConfig
    sqlite: SQLiteConfig
    logging: dict[str, Any]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, with override values taking precedence."""
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
    default_config_path = Path(__file__).parent / "default_config.yaml"
    with open(default_config_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    config_data["host"] = args.host
    config_data["port"] = args.port
    config_data["lean"]["concurrency"] = args.concurrency

    if args.config is not None:
        override_path = Path(args.config)
        if override_path.exists():
            with open(override_path, encoding="utf-8") as f:
                override_data = yaml.safe_load(f)
            config_data = _deep_merge(config_data, override_data)

    config = Config.model_validate(config_data)

    config.host = args.host
    config.port = args.port

    if args.log_level:
        if "handlers" in config.logging:
            for handler in config.logging["handlers"].values():
                if isinstance(handler, dict):
                    handler["level"] = args.log_level.upper()
        if "loggers" in config.logging:
            for logger in config.logging["loggers"].values():
                if isinstance(logger, dict):
                    logger["level"] = args.log_level.upper()

    if args.lean_workspace != "default":
        config.lean.workspace = args.lean_workspace

    return config
