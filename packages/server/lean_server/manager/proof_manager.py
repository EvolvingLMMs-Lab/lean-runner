import asyncio
import logging

from ..database.proof import ProofDatabase
from ..proof.lean import LeanProof
from ..proof.proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class ProofManager:
    def __init__(
        self,
        *,
        proof_database: ProofDatabase,
        lean_semaphore: asyncio.Semaphore,
        background_tasks: set[asyncio.Task],
    ):
        self.proof_database = proof_database
        self.lean_semaphore = lean_semaphore
        self.background_tasks = background_tasks

    async def submit_proof(
        self,
        *,
        proof: LeanProof,
        config: LeanProofConfig,
    ):
        task = asyncio.create_task(self.run_proof(proof=proof, config=config))
        logger.info(f"Submitted proof: {proof.proof_id}")
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        return {"id": proof.proof_id}

    async def run_proof(
        self, *, proof: LeanProof, config: LeanProofConfig
    ) -> dict | None:
        await self.proof_database.update_status(
            proof_id=proof.proof_id, status=LeanProofStatus.PENDING
        )
        async with self.lean_semaphore:
            try:
                logger.info(f"Running proof: {proof}")
                logger.info(f"Config: {config}")
                result = await proof.execute(config, proof_database=self.proof_database)
                logger.info(f"Proof result: {result}")
                await self.proof_database.insert_proof(
                    proof=proof, config=config, result=result
                )
                logger.info("Proof result inserted into database")
                return {
                    "status": "success",
                    "id": proof.proof_id,
                    "result": result,
                }
            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.error(f"Error running proof: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                }

    async def get_result(self, proof_id: str) -> LeanProofResult:
        return await self.proof_database.get_result(proof_id)
