import aiohttp
import json
from typing import Any, Dict, Optional


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
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Initializes or returns the aiohttp client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def check_proof(
        self, proof: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sends a proof to the /prove/check endpoint.

        Args:
            proof: The proof string to be checked.
            config: An optional dictionary for proof configuration.

        Returns:
            A dictionary containing the server's response.
        """
        session = await self._get_session()
        url = f"{self.base_url}prove/check"

        data = {"proof": proof, "config": json.dumps(config) if config else "{}"}

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
