import asyncio
import logging

from ..database.proof import ProofDatabase
from ..proof.config import LeanProofConfig
from ..proof.lean import LeanProof

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
            uuid = uuid()
            task = asyncio.create_task(self.run_proof(proof=proof))
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            return task

    async def run_proof(
        self, *, proof: LeanProof, config: LeanProofConfig
    ) -> dict | None:
        async with self.lean_semaphore:
            try:
                logger.info(f"Running proof: {proof}")
                logger.info(f"Config: {config}")
                result = await proof.execute(config)
                logger.info(f"Proof result: {result}")
                id = await self.proof_database.insert_proof(proof, config, result)
                logger.info("Proof result inserted into database")
                return {
                    "status": "success",
                    "id": id,
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
