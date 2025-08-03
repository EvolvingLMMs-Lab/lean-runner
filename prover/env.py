from pathlib import Path
import yaml
from pydantic import BaseModel

class LeanConfig(BaseModel):
    executable: str
    workspace: str

class Config(BaseModel):
    lean: LeanConfig

with open(Path(__file__).parents[1] / "config.yaml", "r") as f:
    config_dict = yaml.safe_load(f)
    CONFIG = Config.model_validate(config_dict)
