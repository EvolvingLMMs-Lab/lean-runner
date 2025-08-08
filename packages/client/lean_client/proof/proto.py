from enum import Enum

from pydantic import BaseModel


class ProofConfig(BaseModel):
    all_tactics: bool = False
    ast: bool = False
    tactics: bool = False
    premises: bool = False
    timeout: float = 3600.0


class LeanProofStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class ProofResult(BaseModel):
    success: bool | None = None
    status: LeanProofStatus
    result: dict | None = None
    error_message: str | None = None


class Proof(BaseModel):
    id: str
