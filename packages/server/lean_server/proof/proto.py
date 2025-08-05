from enum import Enum

from pydantic import BaseModel


class LeanProofConfig(BaseModel):
    all_tactics: bool = False
    ast: bool = False
    tactics: bool = False
    premises: bool = False


class LeanProofStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class LeanProofResult(BaseModel):
    status: LeanProofStatus
    result: dict | None = None
    error_message: str | None = None
