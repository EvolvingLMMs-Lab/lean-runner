import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from lean_server.database.proof import ProofDatabase
from lean_server.manager.proof_manager import ProofManager

logger = logging.getLogger(__name__)


def get_lifespan(*, concurrency: int):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting Lean Server")
        app.state.lean_semaphore = asyncio.Semaphore(concurrency)
        
        app.state.background_tasks = set()
        
        app.state.proof_database = ProofDatabase()
        await app.state.proof_database.create_table()

        app.state.proof_manager = ProofManager(
            proof_database=app.state.proof_database,
            lean_semaphore=app.state.lean_semaphore,
            background_tasks=app.state.background_tasks,
        )

        yield

        logger.info("Lean Server is shutting down")

    return lifespan
