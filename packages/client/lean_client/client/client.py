import json
import logging
import os
from pathlib import Path

import httpx

from ..proof.proto import Proof, ProofConfig, ProofResult
from .aio.client import AsyncLeanClient

logger = logging.getLogger(__name__)


class LeanClient:
    """
    A client for interacting with the Lean Server API.

    This client provides both synchronous and asynchronous methods for making API calls.
    The asynchronous client is available via the `aio` attribute.
    """

    def __init__(self, base_url: str, timeout: float = 3600.0):
        """
        Initializes the LeanClient.

        Args:
            base_url: The base URL of the Lean Server, e.g., "http://localhost:8000".
            timeout: The timeout for the HTTP requests in seconds.
        """
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.timeout = timeout
        self.aio = AsyncLeanClient(base_url, timeout)
        self._session: httpx.Client | None = None

    def _get_session(self) -> httpx.Client:
        """Initializes or returns the httpx client session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(timeout=self.timeout, base_url=self.base_url)
        return self._session

    def _get_proof_content(self, file_or_content: str | Path | os.PathLike) -> str:
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
                - A string containing the proof
                - A Path object pointing to a file containing the proof
                - A string path to a file containing the proof
            config: An optional dictionary for proof configuration.

        Returns:
            A Proof object representing the submitted job.
        """
        session = self._get_session()

        proof_content = self._get_proof_content(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        response = session.post("/prove/submit", data=data)
        response.raise_for_status()
        print(response.json())
        return Proof.model_validate(response.json())

    def verify(
        self, proof: str | Path | os.PathLike, config: ProofConfig | None = None
    ) -> ProofResult:
        """
        Sends a proof to the /prove/check endpoint synchronously.

        Args:
            proof: The proof content. Can be:
                - A string containing the proof
                - A Path object pointing to a file containing the proof
                - A string path to a file containing the proof
            config: An optional dictionary for proof configuration.

        Returns:
            A dictionary containing the server's response.
        """
        session = self._get_session()

        proof_content = self._get_proof_content(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        response = session.post("/prove/check", data=data)
        response.raise_for_status()

        return ProofResult.model_validate(response.json())

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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
