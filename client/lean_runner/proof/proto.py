from enum import Enum

from pydantic import BaseModel, Field

from ..grpc import prove_pb2


class ProofConfig(BaseModel):
    """Configuration for a proof verification request."""

    all_tactics: bool = Field(False, description="Whether to return all tactics.")
    ast: bool = Field(False, description="Whether to return the abstract syntax tree.")
    tactics: bool = Field(False, description="Whether to return tactics.")
    premises: bool = Field(False, description="Whether to return premises.")
    timeout: float = Field(
        3600.0, description="The timeout for the verification in seconds."
    )
    memory_limit: int = Field(
        8192 * 1024 * 1024, description="Memory limit in bytes for the Lean process."
    )
    cpu_time_limit: float = Field(
        300.0, description="The CPU time limit for the verification in seconds."
    )
    stack_limit: int = Field(
        1024 * 1024 * 1024, description="The stack size limit in bytes."
    )
    file_size_limit: int = Field(
        1024 * 1024 * 1024, description="The file size limit in bytes."
    )
    num_file_limit: int = Field(1024, description="The number of open files limit.")

    def to_protobuf(self) -> prove_pb2.ProofConfig:
        """Convert Pydantic ProofConfig to protobuf ProofConfig."""
        pb_config = prove_pb2.ProofConfig()
        pb_config.all_tactics = self.all_tactics
        pb_config.ast = self.ast
        pb_config.tactics = self.tactics
        pb_config.premises = self.premises
        pb_config.timeout.seconds = int(self.timeout)
        pb_config.timeout.nanos = int(
            (self.timeout - int(self.timeout)) * 1_000_000_000
        )
        pb_config.memory_limit = self.memory_limit
        pb_config.cpu_time_limit.seconds = int(self.cpu_time_limit)
        pb_config.cpu_time_limit.nanos = int(
            (self.cpu_time_limit - int(self.cpu_time_limit)) * 1_000_000_000
        )
        pb_config.stack_limit = self.stack_limit
        pb_config.file_size_limit = self.file_size_limit
        pb_config.num_file_limit = self.num_file_limit
        return pb_config


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

    proof_id: str = Field(..., description="The unique identifier for the proof task.")
    success: bool | None = Field(
        None,
        description="Whether the proof was successful. Can be None if not finished.",
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
