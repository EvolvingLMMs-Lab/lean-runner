import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx
from anyio import Path as AnyioPath

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
            self._session = httpx.AsyncClient(timeout=self.timeout)
        return self._session

    async def _read_proof_from_file(self, file_path: str | Path | AnyioPath) -> str:
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
        path = AnyioPath(file_path)
        if not await path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            return await path.read_text(encoding="utf-8")
        except OSError as e:
            raise OSError(f"Error reading file {path}: {e}") from e

    async def verify(
        self,
        proof: str | Path | os.PathLike | AnyioPath,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Sends a proof to the /prove/check endpoint.

        Args:
            proof: The proof content. Can be:
                - A string containing the proof
                - A Path object pointing to a file containing the proof
                - A string path to a file containing the proof
            config: An optional dictionary for proof configuration.

        Returns:
            A dictionary containing the server's response.
        """
        session = await self._get_session()
        url = f"{self.base_url}prove/check"

        if isinstance(proof, str | Path | os.PathLike):
            path = AnyioPath(proof)
            if await path.exists() and await path.is_file():
                proof_content = await self._read_proof_from_file(path)
            else:
                proof_content = str(proof)
        else:
            proof_content = str(proof)

        data = {
            "proof": proof_content,
            "config": json.dumps(config) if config else "{}",
        }

        try:
            response = await session.post(url, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            try:
                return response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response.text}")
                return {"error": str(e), "status": "N/A"}
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

    async def close(self):
        """Closes the client session."""
        if self._session and not self._session.is_closed:
            await self._session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
