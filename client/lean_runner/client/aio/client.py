import asyncio
import logging
import os
from collections.abc import AsyncIterable, Iterable
from pathlib import Path

import anyio
import grpc
import tqdm

from ...grpc import prove_pb2, prove_pb2_grpc
from ...proof.proto import ProofConfig, ProofResult

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
        self, file_or_content: str | Path | os.PathLike | anyio.Path
    ) -> str:
        """
        Gets the content of a proof.

        If `file_or_content` is a path to an existing file, it reads the file's content.
        Otherwise, it returns the string content directly.
        """
        if isinstance(file_or_content, Path | os.PathLike | anyio.Path) or (
            isinstance(file_or_content, str) and "\n" not in file_or_content
        ):
            try:
                path = anyio.Path(file_or_content)
                if await path.exists():
                    async with await path.open(encoding="utf-8") as f:
                        return await f.read()
                else:
                    return str(file_or_content)
            except (OSError, ValueError):
                pass

        return str(file_or_content)

    async def verify(
        self,
        proof: str | Path | os.PathLike | anyio.Path,
        config: ProofConfig | None = None,
    ) -> ProofResult:
        """
        Sends a proof to the server for synchronous verification.
        """
        stub = self._get_stub()
        proof_content = await self._get_proof_content(proof)
        config = config or ProofConfig()

        pb_config = config.to_protobuf()

        request = prove_pb2.CheckProofRequest(proof=proof_content, config=pb_config)
        response = await stub.CheckProof(request)
        return ProofResult.from_protobuf(response)

    async def verify_all(
        self,
        proofs: Iterable[str | Path | os.PathLike | anyio.Path]
        | AsyncIterable[str | Path | os.PathLike | anyio.Path],
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
        try:
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
        except Exception as e:
            logger.error(f"Error verifying proofs: {e}")
            raise e
        finally:
            pbar.close()

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
