from fastapi import FastAPI, HTTPException


def launch_health_router(app: FastAPI):
    @app.get("/health")
    async def health():
        try:
            return {"status": "ok", "message": "Lean Server is running", "version": "0.0.1"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e