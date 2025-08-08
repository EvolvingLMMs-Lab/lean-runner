import logging

from fastapi import FastAPI, Form, HTTPException

from lean_server.manager.proof_manager import ProofManager
from lean_server.proof.lean import LeanProof
from lean_server.proof.proto import LeanProofConfig

logger = logging.getLogger(__name__)


def launch_prove_router(app: FastAPI):
    @app.post("/prove/check")
    async def check_proof(
        *,
        proof: str = Form(...),
        config: str = Form(default="{}"),
    ):
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
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.get("/prove/result/{proof_id}")
    async def get_result(
        *,
        proof_id: str,
    ):
        proof_manager: ProofManager = app.state.proof_manager
        result = await proof_manager.get_result(proof_id)
        return result
