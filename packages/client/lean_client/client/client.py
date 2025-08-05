import json
import os
from pathlib import Path

import httpx

from ..proof.proto import ProofConfig, ProofResult
from .aio.client import AsyncLeanClient


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
            self._session = httpx.Client(timeout=self.timeout)
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
        url = f"{self.base_url}prove/check"

        proof_content = self._get_proof_content(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        try:
            response = session.post(url, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return ProofResult.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            return ProofResult(
                error_message=str(e),
                status=e.response.status_code,
                result=None,
            )
        except httpx.RequestError as e:
            # Handle connection errors
            return ProofResult(
                error_message=str(e),
                status="N/A",
            )

    def close(self):
        """Closes the client session."""
        if self._session and not self._session.is_closed:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
