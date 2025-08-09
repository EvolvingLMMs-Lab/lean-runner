import uvicorn
from fastapi import FastAPI

from ..config import Config, get_config
from .args import parse_args
from .db import launch_db_router
from .lifespan import get_lifespan
from .prove import launch_prove_router


def launch(*, config: Config) -> FastAPI:
    app = FastAPI(lifespan=get_lifespan(config=config))
    launch_prove_router(app)
    launch_db_router(app)
    return app


def main():
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
