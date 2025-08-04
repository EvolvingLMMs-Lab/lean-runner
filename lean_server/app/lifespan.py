import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def get_lifespan(*, concurrency: int):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting Lean Server")
        app.state.lean_semaphore = asyncio.Semaphore(concurrency)
        pass
        logger.info("Lean Server is shutting down")

    return lifespan
