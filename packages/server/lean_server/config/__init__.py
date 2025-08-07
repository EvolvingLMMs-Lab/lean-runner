import copy
from pathlib import Path

import yaml

from .config import Config

with open(Path(__file__).parent / "config.yaml") as f:
    config_dict = yaml.safe_load(f)
    CONFIG = Config.model_validate(config_dict)


def get_logging_config_with_level(log_level: str) -> dict:
    """Get logging configuration with specified log level."""
    logging_config = copy.deepcopy(CONFIG.logging)

    # Update all handlers to use the specified log level
    if "handlers" in logging_config:
        for _, handler_config in logging_config["handlers"].items():
            handler_config["level"] = log_level

    # Update all loggers to use the specified log level
    if "loggers" in logging_config:
        for _, logger_config in logging_config["loggers"].items():
            logger_config["level"] = log_level

    return logging_config
