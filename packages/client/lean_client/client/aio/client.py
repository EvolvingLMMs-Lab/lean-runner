import json
import logging
import os
from pathlib import Path

import httpx
from anyio import Path as AnyioPath

from ...proof.proto import ProofConfig, ProofResult, Proof

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
            self._session = httpx.AsyncClient(timeout=self.timeout, base_url=self.base_url  )
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

    async def close(self):
        if self._session and not self._session.is_closed:
            await self._session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
