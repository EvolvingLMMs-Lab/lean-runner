import uvicorn
from fastapi import FastAPI

from ..config import CONFIG
from .args import parse_args
from .lifespan import get_lifespan
from .prove import router as prove_router


def launch() -> FastAPI:
    app = FastAPI(lifespan=get_lifespan())
    app.include_router(prove_router)
    return app


app = launch()


def main():
    args = parse_args()
    uvicorn.run(
        f"{__name__}:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_config=CONFIG.logging,
    )


if __name__ == "__main__":
    main()
