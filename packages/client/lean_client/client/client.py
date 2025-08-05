import json
import os
from pathlib import Path
from typing import Any

import httpx


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
        self._session: httpx.Client | None = None

    def _get_session(self) -> httpx.Client:
        """Initializes or returns the httpx client session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(timeout=self.timeout)
        return self._session

    def _read_proof_from_file(self, file_path: str | Path) -> str:
        """
        Reads proof content from a file.

        Args:
            file_path: Path to the file containing the proof.

        Returns:
            The content of the file as a string.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            IOError: If there's an error reading the file.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise OSError(f"Error reading file {path}: {e}") from e

    def verify(
        self, proof: str | Path | os.PathLike, config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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

        # Handle different input types for proof
        if isinstance(proof, str | Path | os.PathLike):
            # Check if it's a file path
            path = Path(proof)
            if path.exists() and path.is_file():
                # It's a file path, read the content
                proof_content = self._read_proof_from_file(path)
            else:
                # It's a string content
                proof_content = str(proof)
        else:
            # Assume it's already a string content
            proof_content = str(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        try:
            response = session.post(url, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": str(e),
                "status": e.response.status_code,
            }
        except httpx.RequestError as e:
            # Handle connection errors
            return {
                "error": str(e),
                "status": "N/A",
            }

    def close(self):
        """Closes the client session."""
        if self._session and not self._session.is_closed:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
