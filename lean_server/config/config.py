from pydantic import BaseModel


class LeanConfig(BaseModel):
    executable: str
    workspace: str


class Config(BaseModel):
    lean: LeanConfig
    logging: dict
