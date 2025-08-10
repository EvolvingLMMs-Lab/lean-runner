"""
This module defines the proof-related API endpoints for the FastAPI application.
"""
from fastapi import FastAPI, Form, HTTPException

from lean_server.manager.proof_manager import ProofManager
from lean_server.proof.lean import LeanProof
from lean_server.proof.proto import LeanProofConfig


def launch_prove_router(app: FastAPI):
    """
    Mounts the proof-related API endpoints to the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.post("/prove/check")
    async def check_proof(
        *,
        proof: str = Form(...),
        config: str = Form(default="{}"),
    ):
        """
        Synchronously check a Lean proof and return the result.

        This endpoint executes the proof immediately and waits for the result.

        Args:
            proof: The Lean code of the proof.
            config: A JSON string representing the LeanProofConfig.

        Returns:
            The result of the proof execution.
        """
        try:
            lean_proof = LeanProof(proof=proof, config=app.state.config)
            lean_proof_config = LeanProofConfig.model_validate_json(config)
            proof_manager: ProofManager = app.state.proof_manager
            result = await proof_manager.run_proof(
                proof=lean_proof, config=lean_proof_config
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.post("/prove/submit")
    async def submit_proof(
        *,
        proof: str = Form(...),
        config: str = Form(default="{}"),
    ):
        """
        Asynchronously submit a Lean proof for execution.

        This endpoint submits the proof to a background task and returns
        a proof ID immediately.

        Args:
            proof: The Lean code of the proof.
            config: A JSON string representing the LeanProofConfig.

        Returns:
            A dictionary containing the proof ID.
        """
        try:
            lean_proof = LeanProof(proof=proof, config=app.state.config)
            lean_proof_config = LeanProofConfig.model_validate_json(config)
            proof_manager: ProofManager = app.state.proof_manager
            result = await proof_manager.submit_proof(
                proof=lean_proof, config=lean_proof_config
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

    @app.get("/prove/result/{proof_id}")
    async def get_result(
        *,
        proof_id: str,
    ):
        """
        Retrieve the result of a previously submitted proof.

        Args:
            proof_id: The ID of the proof.

        Returns:
            The result of the proof execution.
        """
        proof_manager: ProofManager = app.state.proof_manager
        result = await proof_manager.get_result(proof_id)
        return result
