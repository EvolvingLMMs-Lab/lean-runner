import asyncio
import logging

from lean_server.database.proof import ProofDatabase
from lean_server.proof.config import LeanProofConfig
from lean_server.proof.lean import LeanProof


logger = logging.getLogger(__name__)


class ProofManager:
    def __init__(self, *, proof_database: ProofDatabase, lean_semaphore: asyncio.Semaphore):
        self.proof_database = proof_database
        self.lean_semaphore = lean_semaphore
    
    async def run_proof(self, *, proof: LeanProof, config: LeanProofConfig) -> dict | None:
        async with self.lean_semaphore:
            try:
                result = await proof.execute(config)
                await self.proof_database.insert_proof(proof, config, result)
                return result
            except Exception as e:
                logger.error(f"Error running proof: {e}")
                return None

