import logging
import os
from collections.abc import Iterable
from concurrent import futures
from functools import partial
from pathlib import Path

import grpc
import tqdm
from google.protobuf.struct_pb2 import Struct

from ..grpc import prove_pb2, prove_pb2_grpc, utils_pb2, utils_pb2_grpc
from ..proof.proto import Proof, ProofConfig, ProofResult

logger = logging.getLogger(__name__)


class LeanClient:
    """
    A client for interacting with the Lean Server via gRPC.

    This client provides both synchronous and asynchronous methods for making API calls.
    The asynchronous client is available via the `aio` attribute.
    """

    def __init__(self, address: str):
        """
        Initializes the LeanClient.

        Args:
            address: The address of the gRPC server, e.g., "localhost:50051".
        """
        self.address = address
        self._channel: grpc.Channel | None = None
        self._stub: prove_pb2_grpc.ProveServiceStub | None = None
        self._utils_stub: utils_pb2_grpc.UtilsServiceStub | None = None

    def _get_channel(self) -> grpc.Channel:
        """Initializes or returns the gRPC channel."""
        if self._channel is None:
            self._channel = grpc.insecure_channel(self.address)
        return self._channel

    def _get_stub(self) -> prove_pb2_grpc.ProveServiceStub:
        """Initializes or returns the gRPC stub."""
        if self._stub is None:
            self._stub = prove_pb2_grpc.ProveServiceStub(self._get_channel())
        return self._stub

    def _get_utils_stub(self) -> utils_pb2_grpc.UtilsServiceStub:
        """Initializes or returns the gRPC utils stub."""
        if self._utils_stub is None:
            self._utils_stub = utils_pb2_grpc.UtilsServiceStub(self._get_channel())
        return self._utils_stub

    def _get_proof_content(self, file_or_content: str | Path | os.PathLike) -> str:
        """
        Gets the content of a proof.

        If `file_or_content` is a path to an existing file, it reads the file's content.
        Otherwise, it returns the string content directly.
        """
        path = Path(file_or_content)
        if not path.exists():
            return str(file_or_content)
        try:
            with path.open(encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise OSError(f"Error reading file {path}: {e}") from e

    def submit(
        self, proof: str | Path | os.PathLike, config: ProofConfig | None = None
    ) -> Proof:
        """
        Submits a proof to the server for asynchronous processing.
        """
        stub = self._get_stub()
        proof_content = self._get_proof_content(proof)
        config = config or ProofConfig()

        # Convert config to a protobuf Struct
        s = Struct()
        s.update(config.model_dump())

        request = prove_pb2.SubmitProofRequest(proof=proof_content, config=s)
        response = stub.SubmitProof(request)
        return Proof(id=response.proof_id)

    def verify(
        self, proof: str | Path | os.PathLike, config: ProofConfig | None = None
    ) -> ProofResult:
        """
        Sends a proof to the server for synchronous verification.
        """
        stub = self._get_stub()
        proof_content = self._get_proof_content(proof)
        config = config or ProofConfig()

        # Convert config to a protobuf Struct
        s = Struct()
        s.update(config.model_dump())

        request = prove_pb2.CheckProofRequest(proof=proof_content, config=s)
        response = stub.CheckProof(request)
        return ProofResult.model_validate(
            {
                "proof_id": response.proof_id,
                "success": response.success,
                "result": response.result,
                "error_message": response.error_message,
            }
        )

    def verify_all(
        self,
        proofs: Iterable[str | Path | os.PathLike],
        config: ProofConfig | None = None,
        total: int | None = None,
        max_workers: int = 128,
        progress_bar: bool = True,
    ) -> Iterable[ProofResult]:
        """
        Verifies a collection of proofs concurrently using a thread pool.
        """
        if total is None and hasattr(proofs, "__len__"):
            total = len(proofs)

        pbar = tqdm.tqdm(total=total, disable=not progress_bar, desc="Verifying proofs")

        def _verify_wrapper(proof_item, proof_config):
            try:
                return self.verify(proof_item, proof_config)
            except Exception as e:
                return e
            finally:
                pbar.update(1)

        with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            verify_func = partial(_verify_wrapper, proof_config=config)
            results_iterator = executor.map(verify_func, proofs)

            for result in results_iterator:
                if isinstance(result, Exception):
                    logger.error(f"Error verifying proof: {result}")
                else:
                    yield result

        pbar.close()

    def get_result(self, proof: Proof) -> ProofResult:
        """
        Retrieves the result of a proof submission.
        """
        stub = self._get_stub()
        request = prove_pb2.GetResultRequest(proof_id=proof.id)
        response = stub.GetResult(request)
        return ProofResult.model_validate(
            {
                "proof_id": response.proof_id,
                "success": response.success,
                "result": response.result,
                "error_message": response.error_message,
            }
        )

    def health_check(self):
        """Checks the health of the server."""
        stub = self._get_utils_stub()
        request = utils_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return stub.Health(request)

    def close(self):
        """Closes the client channel."""
        if self._channel:
            self._channel.close()

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, ensuring the channel is closed."""
        self.close()
