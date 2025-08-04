
from pathlib import Path

import yaml

from .config import Config

with open(Path(__file__).parents[2] / "config.yaml") as f:
    config_dict = yaml.safe_load(f)
    CONFIG = Config.model_validate(config_dict)