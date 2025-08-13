"""
This module defines the lifespan manager for the FastAPI application.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from lean_server.config import Config
from lean_server.database.proof import ProofDatabase
from lean_server.manager.proof_manager import ProofManager

logger = logging.getLogger(__name__)


def get_lifespan(*, config: Config):
    """
    Returns an asynchronous context manager for the application's lifespan.

    This function sets up resources on startup and cleans them up on shutdown.
    It initializes the database, proof manager, and other application state.

    Args:
        config: The application configuration.

    Returns:
        An async context manager function.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        The actual lifespan context manager.

        Args:
            app: The FastAPI application instance.
        """
        # Startup
        logger.info("Starting Lean Server")
        app.state.lean_semaphore = asyncio.Semaphore(config.lean.concurrency)
        app.state.background_tasks = set()
        app.state.config = config

        # Initialize database
        app.state.proof_database = ProofDatabase(
            database_path=config.sqlite.database_path,
            timeout=config.sqlite.timeout,
        )
        await app.state.proof_database.create_table()

        # Initialize proof manager
        app.state.proof_manager = ProofManager(
            proof_database=app.state.proof_database,
            lean_semaphore=app.state.lean_semaphore,
            background_tasks=app.state.background_tasks,
        )

        yield

        # Shutdown
        logger.info("Lean Server is shutting down")

    return lifespan
