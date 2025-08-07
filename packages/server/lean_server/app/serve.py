import uvicorn
from fastapi import FastAPI

from ..config import get_logging_config_with_level
from .args import parse_args
from .lifespan import get_lifespan
from .prove import launch_prove_router


def launch(*, concurrency: int) -> FastAPI:
    app = FastAPI(lifespan=get_lifespan(concurrency=concurrency))
    launch_prove_router(app)
    return app


args = parse_args()
app = launch(concurrency=args.concurrency)


def main():
    # Get logging configuration with the specified log level
    logging_config = get_logging_config_with_level(args.log_level)

    uvicorn.run(
        "lean_server.app.serve:app",
        reload=args.reload,
        host=args.host,
        port=args.port,
        log_config=logging_config,
    )


if __name__ == "__main__":
    main()
