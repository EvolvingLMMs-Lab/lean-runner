"""
This module is the main entry point for launching the Lean server.
"""

import uvicorn
from fastapi import FastAPI

from ..config import Config, get_config
from .args import parse_args
from .db import launch_db_router
from .lifespan import get_lifespan
from .prove import launch_prove_router
from .utils import launch_health_router


def launch(*, config: Config) -> FastAPI:
    """
    Creates and configures the FastAPI application.

    This function initializes the FastAPI app, sets up the lifespan manager,
    and mounts the API routers.

    Args:
        config: The application configuration.

    Returns:
        The configured FastAPI application instance.
    """
    app = FastAPI(lifespan=get_lifespan(config=config))
    launch_health_router(app)
    launch_prove_router(app)
    launch_db_router(app)
    return app


def main():
    """
    The main entry point for the server.

    This function parses command-line arguments, loads the configuration,
    launches the FastAPI application, and starts the Uvicorn server.
    """
    args = parse_args()
    config = get_config(args)
    app = launch(config=config)
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_config=config.logging,
    )


if __name__ == "__main__":
    main()
