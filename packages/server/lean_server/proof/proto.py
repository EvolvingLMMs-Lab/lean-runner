from enum import Enum

from pydantic import BaseModel, Field


class LeanProofConfig(BaseModel):
    """Configuration for a Lean proof request."""

    all_tactics: bool = Field(False, description="Whether to return all tactics.")
    ast: bool = Field(False, description="Whether to return the abstract syntax tree.")
    tactics: bool = Field(False, description="Whether to return tactics.")
    premises: bool = Field(False, description="Whether to return premises.")
    timeout: float = Field(300.0, description="Timeout for the proof in seconds.")


class LeanProofStatus(Enum):
    """The status of a Lean proof."""

    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class LeanProofResult(BaseModel):
    """The result of a Lean proof request."""

    success: bool | None = Field(None, description="Whether the proof was successful.")
    status: LeanProofStatus = Field(..., description="The status of the proof.")
    result: dict | None = Field(None, description="The result of the proof.")
    error_message: str | None = Field(
        None, description="Error message if the proof failed."
    )
