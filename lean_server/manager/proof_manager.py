import asyncio
import logging

from lean_server.database.proof import ProofDatabase
from lean_server.proof.config import LeanProofConfig
from lean_server.proof.lean import LeanProof

logger = logging.getLogger(__name__)


class ProofManager:
    def __init__(
        self, *, proof_database: ProofDatabase, lean_semaphore: asyncio.Semaphore
    ):
        self.proof_database = proof_database
        self.lean_semaphore = lean_semaphore

    async def run_proof(
        self, *, proof: LeanProof, config: LeanProofConfig
    ) -> dict | None:
        async with self.lean_semaphore:
            try:
                logger.info(f"Running proof: {proof}")
                logger.info(f"Config: {config}")
                result = await proof.execute(config)
                logger.info(f"Proof result: {result}")
                await self.proof_database.insert_proof(proof, config, result)
                logger.info(f"Proof result inserted into database")
                return result
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error running proof: {e}")
                return None
