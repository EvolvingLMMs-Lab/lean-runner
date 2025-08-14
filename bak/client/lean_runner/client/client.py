import logging
import os
from collections.abc import Iterable
from concurrent import futures
from functools import partial
from pathlib import Path

import httpx
import tqdm

from ..proof.proto import Proof, ProofConfig, ProofResult
from .aio.client import AsyncLeanClient

logger = logging.getLogger(__name__)


class LeanClient:
    """
    A client for interacting with the Lean Server API.

    This client provides both synchronous and asynchronous methods for making API calls.
    The asynchronous client is available via the `aio` attribute.
    """

    def __init__(self, base_url: str):
        """
        Initializes the LeanClient.

        Args:
            base_url: The base URL of the Lean Server, e.g., "http://localhost:8000".
        """
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.aio = AsyncLeanClient(base_url)
        self._session: httpx.Client | None = None

    def _get_session(self) -> httpx.Client:
        """Initializes or returns the httpx client session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(base_url=self.base_url)
        return self._session

    def _get_proof_content(self, file_or_content: str | Path | os.PathLike) -> str:
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
        Submits a proof to the /prove/submit endpoint synchronously.

        Args:
            proof: The proof content. Can be:
                - A string containing the proof.
                - A Path object pointing to a file containing the proof.
                - A string path to a file containing the proof.
            config: An optional dictionary for proof configuration.

        Returns:
            A Proof object representing the submitted job.
        """
        session = self._get_session()

        proof_content = self._get_proof_content(proof)
        config = config or ProofConfig()

        data = {
            "proof": proof_content,
            "config": config.model_dump_json(),
        }

        response = session.post("/prove/submit", data=data)
        response.raise_for_status()
        return Proof.model_validate(response.json())

    def verify(
        self, proof: str | Path | os.PathLike, config: ProofConfig | None = None
    ) -> ProofResult:
        """
        Sends a proof to the /prove/check endpoint synchronously.

        Args:
            proof: The proof content. Can be:
                - A string containing the proof.
                - A Path object pointing to a file containing the proof.
                - A string path to a file containing the proof.
            config: An optional dictionary for proof configuration.

        Returns:
            A dictionary containing the server's response.
        """
        session = self._get_session()

        proof_content = self._get_proof_content(proof)

        if config is None:
            config = ProofConfig()

        data = {"proof": proof_content, "config": config.model_dump_json()}

        response = session.post("/prove/check", data=data, timeout=config.timeout)
        response.raise_for_status()

        return ProofResult.model_validate(response.json())

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

        This function is designed to be memory-efficient. It yields results as
        they are completed, making it suitable for very large collections of proofs.

        Args:
            proofs: An iterable of proofs to verify.
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

        # To handle exceptions gracefully with executor.map, we wrap the call.
        def _verify_wrapper(proof_item, proof_config):
            try:
                return self.verify(proof_item, proof_config)
            except Exception as e:
                return e
            finally:
                pbar.update(1)

        with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Use partial to fix the `config` argument for the wrapper.
            verify_func = partial(_verify_wrapper, proof_config=config)

            results_iterator = executor.map(verify_func, proofs)

            for result in results_iterator:
                if isinstance(result, Exception):
                    import traceback

                    traceback.print_exc()
                    logger.error(f"Error verifying proof: {result}")
                else:
                    yield result

        pbar.close()

    def get_result(self, proof: Proof) -> ProofResult:
        """
        Retrieves the result of a proof submission.

        Args:
            proof: A Proof object.

        Returns:
            A ProofResult object.
        """
        session = self._get_session()
        response = session.get(f"/prove/result/{proof.id}")
        response.raise_for_status()
        return ProofResult.model_validate(response.json())

    def close(self):
        """Closes the client session."""
        if self._session and not self._session.is_closed:
            self._session.close()

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, ensuring the session is closed."""
        self.close()
