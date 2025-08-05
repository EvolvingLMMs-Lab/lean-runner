import asyncio
import logging

from ..database.proof import ProofDatabase
from ..proof.lean import LeanProof
from ..proof.proto import LeanProofConfig
from ..utils.uuid.uuid import uuid

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
        async with self.lean_semaphore:
            proof_id = uuid()
            task = asyncio.create_task(
                self.run_proof(proof_id=proof_id, proof=proof, config=config)
            )
            logger.info(f"Submitted proof: {proof_id}")
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            return proof_id

    async def run_proof(
        self, *, proof_id: str | None = None, proof: LeanProof, config: LeanProofConfig
    ) -> dict | None:
        async with self.lean_semaphore:
            try:
                logger.info(f"Running proof: {proof}")
                logger.info(f"Config: {config}")
                result = await proof.execute(config)
                logger.info(f"Proof result: {result}")
                if proof_id is None:
                    proof_id = uuid()
                await self.proof_database.insert_proof(
                    proof=proof, config=config, result=result, proof_id=proof_id
                )
                logger.info("Proof result inserted into database")
                return {
                    "status": "success",
                    "id": proof_id,
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
