import os
from pydantic import BaseModel


class LeanConfig(BaseModel):
    executable: str
    workspace: str

    def __post_init__(self):
        if not os.path.exists(self.workspace):
            raise FileNotFoundError(f"Lean workspace {self.workspace} does not exist")
        if not os.path.exists(self.executable):
            raise FileNotFoundError(f"Lean executable {self.executable} does not exist")


class Config(BaseModel):
    lean: LeanConfig

