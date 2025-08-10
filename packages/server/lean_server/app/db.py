"""
This module defines the database API endpoints for the FastAPI application.
"""
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..database.proof import ProofDatabase


def launch_db_router(app: FastAPI):
    """
    Mounts the database-related API endpoints to the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.get("/db/fetch")
    async def fetch_dataset(
        query: str = Query(default="SELECT * FROM proof"),
        batch_size: int = Query(default=100),
    ):
        """
        Fetch data from the database using a SQL query with efficient batch processing.
        Returns results as a streaming JSON response.

        Args:
            query: The SQL query to execute.
            batch_size: The number of rows to fetch per batch.

        Returns:
            A streaming response containing the query results in JSON format.
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
    async def clean_db(seconds: int = Query(default=0)):
        """
        Clean the database by removing old proof records and orphaned status entries.

        Args:
            seconds: The minimum age in seconds for records to be deleted.
                     (Currently unused, defaults to 24 hours in the implementation).

        Returns:
            A confirmation message.
        """
        try:
            proof_database: ProofDatabase = app.state.proof_database
            await proof_database.clean_db(seconds)
            return {"message": "Database cleaned successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database cleanup failed: {str(e)}"
            ) from e
