import asyncio
import logging
import os
from collections.abc import AsyncIterable, Iterable
from pathlib import Path

import httpx
import tqdm
from anyio import Path as AnyioPath

from ...proof.proto import Proof, ProofConfig, ProofResult

logger = logging.getLogger(__name__)


class AsyncLeanClient:
    """
    An asynchronous client for interacting with the Lean Server API.
    """

    def __init__(self, base_url: str, timeout: float = 300.0):
        """
        Initializes the AsyncLeanClient.

        Args:
            base_url: The base URL of the Lean Server, e.g., "http://localhost:8000".
            timeout: The timeout for HTTP requests in seconds.
        """
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.timeout = timeout
        self._session: httpx.AsyncClient | None = None

    async def _get_session(self) -> httpx.AsyncClient:
        """Initializes or returns the httpx async client session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                timeout=self.timeout, base_url=self.base_url
            )
        return self._session

    async def _get_proof_content(
        self, file_or_content: str | Path | os.PathLike | AnyioPath
    ) -> str:
        """
        Gets the content of a proof.

        If `file_or_content` is a path to an existing file, it reads the file's content.
        Otherwise, it returns the string content directly.

        Args:
            file_or_content: The proof content or a path to the proof file.

        Returns:
            The string content of the proof.

        Raises:
            OSError: If there is an error reading the file.
        """
        path = AnyioPath(file_or_content)
        if not await path.exists():
            return str(file_or_content)

        try:
            return await path.read_text(encoding="utf-8")
        except OSError as e:
            raise OSError(f"Error reading file {path}: {e}") from e

    async def submit(
        self,
        proof: str | Path | os.PathLike | AnyioPath,
        config: ProofConfig | None = None,
    ) -> Proof:
        """
        Submits a proof asynchronously.

        This method sends the proof to the server's `/prove/submit` endpoint and
        immediately returns a `Proof` object containing the task ID. The result
        can be retrieved later using the `get_result` method with this ID.

        Args:
            proof: The proof content, which can be a string, Path, or os.PathLike object.
            config: The proof configuration.

        Returns:
            A `Proof` object representing the submitted task.
        """
        session = await self._get_session()

        proof_content = await self._get_proof_content(proof)
        config = config or ProofConfig()

        data = {
            "proof": proof_content,
            "config": config.model_dump_json(),
        }

        response = await session.post("/prove/submit", data=data)
        response.raise_for_status()

        return Proof.model_validate(response.json())

    async def verify(
        self,
        proof: str | Path | os.PathLike | AnyioPath,
        config: ProofConfig | None = None,
    ) -> ProofResult:
        """
        Verifies a proof asynchronously.

        This method sends the proof to the server's `/prove/check` endpoint and
        waits for the server to return the verification result. This is a
        blocking call that waits for the verification to complete.

        Args:
            proof: The proof content, which can be a string, Path, or os.PathLike object.
            config: The proof configuration.

        Returns:
            A `ProofResult` object containing the verification result.
        """
        session = await self._get_session()

        proof_content = await self._get_proof_content(proof)
        config = config or ProofConfig()

        data = {
            "proof": proof_content,
            "config": config.model_dump_json(),
        }

        response = await session.post("/prove/check", data=data, timeout=config.timeout)
        response.raise_for_status()

        return ProofResult.model_validate(response.json())

    async def verify_all(
        self,
        proofs: Iterable[str | Path | os.PathLike | AnyioPath]
        | AsyncIterable[str | Path | os.PathLike | AnyioPath],
        config: ProofConfig | None = None,
        total: int | None = None,
        max_workers: int = 128,
        progress_bar: bool = True,
    ) -> AsyncIterable[ProofResult]:
        """
        Verifies a collection of proofs concurrently using a producer-consumer model.

        This function is designed to be memory-efficient. It uses a bounded queue
        to prevent the producer from reading the entire iterator into memory, making
        it suitable for very large collections of proofs.

        Args:
            proofs: An iterable or async iterable of proofs to verify.
            config: The proof configuration.
            total: The total number of proofs (for the progress bar). If not provided,
                   it's inferred from `len(proofs)` if available.
            max_workers: The maximum number of concurrent verification tasks
                    (consumers).
            progress_bar: Whether to display a progress bar.

        Yields:
            ProofResult: The result of each verification as it completes.
        """
        if total is None and hasattr(proofs, "__len__"):
            total = len(proofs)

        # The queue for proofs to be processed. `maxsize` provides back-pressure.
        proof_queue = asyncio.Queue(maxsize=max_workers)
        # The queue for completed results.
        results_queue = asyncio.Queue()
        pbar = tqdm.tqdm(total=total, disable=not progress_bar, desc="Verifying proofs")

        # Consumer: A worker that pulls proofs from the queue and verifies them.
        async def worker():
            while True:
                proof = await proof_queue.get()
                if proof is None:
                    # Sentinel value received, exit the loop.
                    proof_queue.task_done()
                    break

                try:
                    result = await self.verify(proof, config)
                    await results_queue.put(result)
                except asyncio.CancelledError:
                    # The worker was cancelled, exit gracefully.
                    break
                except Exception as e:
                    # Log the error and place an exception object on the results queue
                    # so the main loop can decide how to handle it.
                    logger.error(f"Error verifying proof: {e}")
                    await results_queue.put(e)
                finally:
                    proof_queue.task_done()

        # Producer: Reads from the source iterator and puts proofs onto the queue.
        async def producer():
            try:
                if isinstance(proofs, AsyncIterable):
                    async for proof in proofs:
                        await proof_queue.put(proof)
                else:
                    for proof in proofs:
                        await proof_queue.put(proof)
            finally:
                # Signal that production is done by putting sentinel values
                # for each worker.
                for _ in range(max_workers):
                    await proof_queue.put(None)

        # Monitor: Waits for all work to be done and signals completion.
        async def monitor():
            await producer_task
            await proof_queue.join()
            await results_queue.put(None)  # Sentinel to signal completion.

        workers = [asyncio.create_task(worker()) for _ in range(max_workers)]
        producer_task = asyncio.create_task(producer())
        monitor_task = asyncio.create_task(monitor())

        processed_count = 0
        try:
            while True:
                if total is not None and processed_count >= total:
                    break

                result = await results_queue.get()
                if result is None:  # Sentinel value means we're done.
                    break

                processed_count += 1
                pbar.update(1)

                if isinstance(result, Exception):
                    # An error occurred in a worker. We can choose to raise it,
                    # log it, or yield it. For now, we just log it again.
                    logger.error(f"Received exception from worker: {result}")
                else:
                    yield result
        finally:
            # Clean up all tasks to prevent "Task was destroyed but it is pending"
            pbar.close()
            producer_task.cancel()
            monitor_task.cancel()
            for w in workers:
                w.cancel()
            await asyncio.gather(
                producer_task, monitor_task, *workers, return_exceptions=True
            )

    async def get_result(self, proof: Proof) -> ProofResult:
        """
        Gets the result of a proof by its task ID.

        Args:
            proof: A `Proof` object containing the task ID.

        Returns:
            A `ProofResult` object containing the proof result.
        """
        session = await self._get_session()
        response = await session.get(f"/prove/result/{proof.id}")
        response.raise_for_status()
        return ProofResult.model_validate(response.json())

    async def close(self):
        """Closes the httpx client session."""
        if self._session and not self._session.is_closed:
            await self._session.aclose()

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, ensuring the session is closed."""
        await self.close()
