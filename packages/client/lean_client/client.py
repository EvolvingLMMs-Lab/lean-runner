import json
import os
from pathlib import Path
from typing import Any, Union

import aiohttp


class LeanClient:
    """
    An asynchronous client for interacting with the Lean Server API.
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
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Initializes or returns the aiohttp client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _read_proof_from_file(self, file_path: Union[str, Path]) -> str:
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
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise IOError(f"Error reading file {path}: {e}")

    async def check_proof(
        self, 
        proof: Union[str, Path, os.PathLike], 
        config: dict[str, Any] | None = None
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

        # Handle different input types for proof
        if isinstance(proof, (str, Path, os.PathLike)):
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

        data = {"proof": proof_content, "config": json.dumps(config) if config else "{}"}

        try:
            async with session.post(url, data=data) as response:
                response.raise_for_status()  # Raise an exception for bad status codes
                return await response.json()
        except aiohttp.ClientError as e:
            # Handle connection errors or bad responses
            return {
                "error": str(e),
                "status": response.status if "response" in locals() else "N/A",
            }

    async def close(self):
        """Closes the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
