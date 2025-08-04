import uvicorn
from fastapi import FastAPI

from ..config import CONFIG
from .args import parse_args

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Lean Server is running."}


def main():
    args = parse_args()
    uvicorn.run(
        "lean_server.cli.serve:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_config=CONFIG.logging,
    )


if __name__ == "__main__":
    main()
