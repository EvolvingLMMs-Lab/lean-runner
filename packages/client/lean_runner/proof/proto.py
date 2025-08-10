from enum import Enum

from pydantic import BaseModel


class ProofConfig(BaseModel):
    """
    Configuration for a proof verification request.

    Attributes:
        all_tactics: Whether to return all tactics.
        ast: Whether to return the abstract syntax tree.
        tactics: Whether to return tactics.
        premises: Whether to return premises.
        timeout: The timeout for the verification in seconds.
    """

    all_tactics: bool = False
    ast: bool = False
    tactics: bool = False
    premises: bool = False
    timeout: float = 300.0


class LeanProofStatus(Enum):
    """
    The status of a Lean proof verification.
    """

    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class ProofResult(BaseModel):
    """
    The result of a proof verification.

    Attributes:
        success: Whether the proof was successful. Can be None if not finished.
        status: The status of the proof verification.
        result: The result data from the verification.
        error_message: An error message if the verification failed.
    """

    success: bool | None = None
    status: LeanProofStatus
    result: dict | None = None
    error_message: str | None = None


class Proof(BaseModel):
    """
    Represents a proof task submitted to the server.

    Attributes:
        id: The unique identifier for the proof task.
    """

    id: str
