from pydantic import BaseModel
from enum import Enum


class LeanProofConfig(BaseModel):
    all_tactics: bool = False
    ast: bool = False
    tactics: bool = False
    premises: bool = False

class LeanProofResult(BaseModel):
    result: dict | None = None
    error_message: str | None = None

class LeanProofStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
