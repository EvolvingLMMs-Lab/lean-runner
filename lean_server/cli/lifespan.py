import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def get_lifespan():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting Lean Server")
        pass
        logger.info("Lean Server is shutting down")

    return lifespan
