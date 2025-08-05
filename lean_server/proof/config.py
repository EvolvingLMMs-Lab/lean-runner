from pydantic import BaseModel


class LeanProofConfig(BaseModel):
    all_tactics: bool = False
    ast: bool = False
    tactics: bool = False
    premises: bool = False
