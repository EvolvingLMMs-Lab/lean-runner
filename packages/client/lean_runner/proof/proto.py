from enum import Enum

from pydantic import BaseModel, Field


class ProofConfig(BaseModel):
    """Configuration for a proof verification request."""

    all_tactics: bool = Field(
        False, description="Whether to return all tactics."
    )
    ast: bool = Field(
        False, description="Whether to return the abstract syntax tree."
    )
    tactics: bool = Field(False, description="Whether to return tactics.")
    premises: bool = Field(False, description="Whether to return premises.")
    timeout: float = Field(
        300.0, description="The timeout for the verification in seconds."
    )


class LeanProofStatus(Enum):
    """
    The status of a Lean proof verification.
    """

    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class ProofResult(BaseModel):
    """The result of a proof verification."""

    success: bool | None = Field(
        None,
        description="Whether the proof was successful. Can be None if not finished.",
    )
    status: LeanProofStatus = Field(
        ..., description="The status of the proof verification."
    )
    result: dict | None = Field(
        None, description="The result data from the verification."
    )
    error_message: str | None = Field(
        None, description="An error message if the verification failed."
    )


class Proof(BaseModel):
    """Represents a proof task submitted to the server."""

    id: str = Field(..., description="The unique identifier for the proof task.")