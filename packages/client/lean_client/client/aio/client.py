import asyncio
import json
import logging
import asyncio
import os
from collections.abc import Iterable, AsyncIterable
from pathlib import Path
import tqdm

import httpx
import tqdm
from anyio import Path as AnyioPath

from ...proof.proto import Proof, ProofConfig, ProofResult

logger = logging.getLogger(__name__)


class AsyncLeanClient:
    """
    An asynchronous client for interacting with the Lean Server API.
    """

    def __init__(self, base_url: str, timeout: float = 3600.0):
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
        session = await self._get_session()

        proof_content = await self._get_proof_content(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        response = await session.post("/prove/submit", data=data)
        response.raise_for_status()

        return Proof.model_validate(response.json())

    async def verify(
        self,
        proof: str | Path | os.PathLike | AnyioPath,
        config: ProofConfig | None = None,
    ) -> ProofResult:
        session = await self._get_session()

        proof_content = await self._get_proof_content(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        response = await session.post("/prove/check", data=data)
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
            max_workers: The maximum number of concurrent verification tasks (consumers).
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
        pbar = tqdm.tqdm(total=total, disable=not progress_bar)

        # Consumer: A worker that pulls proofs from the queue and verifies them.
        async def worker():
            while True:
                try:
                    proof = await proof_queue.get()
                    result = await self.verify(proof, config)
                    await results_queue.put(result)
                except asyncio.CancelledError:
                    # The worker was cancelled, exit gracefully.
                    break
                except Exception as e:
                    # Log the error and place an exception object on the results queue
                    # so the main loop can decide how to handle it.
                    import traceback
                    traceback.print_exc()
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

        workers = [asyncio.create_task(worker()) for _ in range(max_workers)]
        producer_task = asyncio.create_task(producer())

        processed_count = 0
        try:
            while processed_count < max_workers:
                result = await results_queue.get()
                if result is None:
                    # A worker has exited after seeing a sentinel.
                    processed_count += 1
                    continue

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
            for w in workers:
                w.cancel()
            await asyncio.gather(producer_task, *workers, return_exceptions=True)

        return AsyncIterable(worker())

        return AsyncIterable(worker())

    async def get_result(self, proof: Proof) -> ProofResult:
        session = await self._get_session()
        response = await session.get(f"/prove/result/{proof.id}")
        response.raise_for_status()
        return ProofResult.model_validate(response.json())

    async def close(self):
        if self._session and not self._session.is_closed:
            await self._session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
