import asyncio
import logging
import os
from collections.abc import AsyncIterable, Iterable
from pathlib import Path

import grpc
import tqdm
from google.protobuf.struct_pb2 import Struct

from ...grpc import prove_pb2, prove_pb2_grpc
from ...proof.proto import Proof, ProofConfig, ProofResult

logger = logging.getLogger(__name__)


class AsyncLeanClient:
    """An asynchronous client for interacting with the Lean Server via gRPC."""

    def __init__(self, address: str):
        """
        Initializes the AsyncLeanClient.

        Args:
            address: The address of the gRPC server, e.g., "localhost:50051".
        """
        self.address = address
        self._channel: grpc.aio.Channel | None = None
        self._stub: prove_pb2_grpc.ProveServiceStub | None = None

    def _get_channel(self) -> grpc.aio.Channel:
        """Initializes or returns the gRPC channel."""
        if self._channel is None:
            self._channel = grpc.aio.insecure_channel(self.address)
        return self._channel

    def _get_stub(self) -> prove_pb2_grpc.ProveServiceStub:
        """Initializes or returns the gRPC stub."""
        if self._stub is None:
            self._stub = prove_pb2_grpc.ProveServiceStub(self._get_channel())
        return self._stub

    async def _get_proof_content(
        self, file_or_content: str | Path | os.PathLike
    ) -> str:
        """
        Gets the content of a proof.

        If `file_or_content` is a path to an existing file, it reads the file's content.
        Otherwise, it returns the string content directly.
        """
        path = Path(file_or_content)
        if not path.exists():
            return str(file_or_content)
        try:
            # This is a synchronous file read, which is generally okay for local files.
            # For true async file I/O, a library like aiofiles would be needed.
            with path.open(encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise OSError(f"Error reading file {path}: {e}") from e

    async def submit(
        self, proof: str | Path | os.PathLike, config: ProofConfig | None = None
    ) -> Proof:
        """
        Submits a proof to the server for asynchronous processing.
        """
        stub = self._get_stub()
        proof_content = await self._get_proof_content(proof)
        config = config or ProofConfig()

        s = Struct()
        s.update(config.model_dump())

        request = prove_pb2.SubmitProofRequest(proof=proof_content, config=s)
        response = await stub.SubmitProof(request)
        return Proof(id=response.proof_id)

    async def verify(
        self, proof: str | Path | os.PathLike, config: ProofConfig | None = None
    ) -> ProofResult:
        """
        Sends a proof to the server for synchronous verification.
        """
        stub = self._get_stub()
        proof_content = await self._get_proof_content(proof)
        config = config or ProofConfig()

        s = Struct()
        s.update(config.model_dump())

        request = prove_pb2.CheckProofRequest(proof=proof_content, config=s)
        response = await stub.CheckProof(request)
        return ProofResult.model_validate(
            {
                "proof_id": response.proof_id,
                "success": response.success,
                "result": response.result,
                "error_message": response.error_message,
            }
        )

    async def verify_all(
        self,
        proofs: Iterable[str | Path | os.PathLike]
        | AsyncIterable[str | Path | os.PathLike],
        config: ProofConfig | None = None,
        total: int | None = None,
        max_workers: int = 128,
        progress_bar: bool = True,
    ) -> AsyncIterable[ProofResult]:
        """
        Verifies a collection of proofs concurrently.

        This function is designed to be memory-efficient. It yields results as
        they are completed, making it suitable for very large collections of proofs.
        It accepts both synchronous and asynchronous iterables for the proofs.

        Args:
            proofs: An iterable or async iterable of proofs to verify.
            config: The proof configuration.
            total: The total number of proofs (for the progress bar). If not provided,
                   it's inferred from `len(proofs)` if available.
            max_workers: The maximum number of concurrent verification tasks.
            progress_bar: Whether to display a progress bar.

        Yields:
            ProofResult: The result of each verification as it completes.
        """
        if total is None and hasattr(proofs, "__len__"):
            total = len(proofs)

        pbar = tqdm.tqdm(total=total, disable=not progress_bar, desc="Verifying proofs")
        tasks = set()

        async def _verify_wrapper(proof_item):
            try:
                return await self.verify(proof_item, config)
            except Exception as e:
                return e
            finally:
                pbar.update(1)

        async def _proof_iterator():
            if isinstance(proofs, AsyncIterable):
                async for proof in proofs:
                    yield proof
            else:
                for proof in proofs:
                    yield proof

        async for proof in _proof_iterator():
            if len(tasks) >= max_workers:
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )
                for future in done:
                    result = future.result()
                    if isinstance(result, Exception):
                        logger.error(f"Error verifying proof: {result}")
                    else:
                        yield result
                tasks = pending

            task = asyncio.create_task(_verify_wrapper(proof))
            tasks.add(task)

        for future in asyncio.as_completed(tasks):
            result = await future
            if isinstance(result, Exception):
                logger.error(f"Error verifying proof: {result}")
            else:
                yield result

        pbar.close()

    async def get_result(self, proof: Proof) -> ProofResult:
        """
        Retrieves the result of a proof submission.
        """
        stub = self._get_stub()
        request = prove_pb2.GetResultRequest(proof_id=proof.id)
        response = await stub.GetResult(request)
        return ProofResult.model_validate(
            {
                "proof_id": response.proof_id,
                "success": response.success,
                "result": response.result,
                "error_message": response.error_message,
            }
        )

    async def close(self):
        """Closes the client channel."""
        if self._channel:
            await self._channel.close()

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, ensuring the channel is closed."""
        await self.close()
