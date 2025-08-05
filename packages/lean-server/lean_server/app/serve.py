import uvicorn
from fastapi import FastAPI

from ..config import CONFIG
from .args import parse_args
from .lifespan import get_lifespan
from .prove import launch_prove_router


def launch(*, concurrency: int) -> FastAPI:
    app = FastAPI(lifespan=get_lifespan(concurrency=concurrency))
    launch_prove_router(app)
    return app


def main():
    args = parse_args()
    uvicorn.run(
        launch(concurrency=args.concurrency),
        host=args.host,
        port=args.port,
        log_config=CONFIG.logging,
    )


if __name__ == "__main__":
    main()
