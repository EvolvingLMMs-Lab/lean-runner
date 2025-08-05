from fastapi import FastAPI, Form

from lean_server.manager.proof_manager import ProofManager
from lean_server.proof.config import LeanProofConfig
from lean_server.proof.lean import LeanProof


def launch_prove_router(app: FastAPI):
    @app.post("/prove/check")
    async def check_proof(
        *,
        proof: str = Form(...),
        config: str = Form(default="{}"),
    ):
        lean_proof = LeanProof(proof=proof)
        lean_proof_config = LeanProofConfig.model_validate_json(config)
        proof_manager: ProofManager = app.state.proof_manager
        result = await proof_manager.run_proof(
            proof=lean_proof, config=lean_proof_config
        )
        return result

    @app.post("/prove/check/background")
    async def check_proof_background(
        *,
        proof: str = Form(...),
        config: str = Form(default="{}"),
    ):
        lean_proof = LeanProof(proof=proof)
        lean_proof_config = LeanProofConfig.model_validate_json(config)
        proof_manager: ProofManager = app.state.proof_manager
        result = await proof_manager.run_proof(
            proof=lean_proof, config=lean_proof_config
        )
