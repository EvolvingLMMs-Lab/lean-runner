import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..database.proof import ProofDatabase


def launch_db_router(app: FastAPI):
    @app.get("/db/fetch")
    async def fetch_dataset(
        query: str = Query(default="SELECT * FROM proof"),
        batch_size: int = Query(default=100),
    ):
        """
        Fetch data from the database using SQL query with efficient batch processing.
        Returns results as a streaming JSON response.
        """
        try:
            proof_database: ProofDatabase = app.state.proof_database

            async def generate_json_stream():
                """Generate JSON stream of results"""
                yield "["
                first_item = True

                async for row in proof_database.fetch(query, batch_size):
                    if not first_item:
                        yield ","
                    yield json.dumps(row)
                    first_item = False

                yield "]"

            return StreamingResponse(
                generate_json_stream(),
                media_type="application/json",
                headers={
                    "Content-Disposition": "attachment; filename=query_results.json"
                },
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database query failed: {str(e)}"
            ) from e

    @app.delete("/db/clean")
    async def clean_db():
        """
        Clean the database by removing old proof records and orphaned status entries.
        """
        try:
            proof_database: ProofDatabase = app.state.proof_database
            await proof_database.clean_db()
            return {"message": "Database cleaned successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database cleanup failed: {str(e)}"
            ) from e
