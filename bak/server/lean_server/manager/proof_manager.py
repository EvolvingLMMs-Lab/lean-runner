"""
Manages the lifecycle of Lean proofs, from submission to execution and result retrieval.
"""

import asyncio
import logging

from ..database.proof import ProofDatabase
from ..proof.lean import LeanProof
from ..proof.proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class ProofManager:
    """
    Handles the submission, execution, and tracking of Lean proofs.

    This class coordinates with the database to store proof data and results.
    It uses a semaphore to limit concurrent proof executions and manages
    background tasks for running proofs asynchronously.

    Attributes:
        proof_database (ProofDatabase): An instance for interacting with the
            proof database.
        lean_semaphore (asyncio.Semaphore): A semaphore to limit concurrent
            Lean processes.
        background_tasks (set[asyncio.Task]): A set of currently running
            background proof tasks.
    """

    def __init__(
        self,
        *,
        proof_database: ProofDatabase,
        lean_semaphore: asyncio.Semaphore,
        background_tasks: set[asyncio.Task],
    ):
        """
        Initializes the ProofManager.

        Args:
            proof_database: The database handler for proofs.
            lean_semaphore: The semaphore to control concurrency.
            background_tasks: A set to manage background asyncio tasks.
        """
        self.proof_database = proof_database
        self.lean_semaphore = lean_semaphore
        self.background_tasks = background_tasks

    async def submit_proof(
        self,
        *,
        proof: LeanProof,
        config: LeanProofConfig,
    ) -> dict[str, str]:
        """
        Submits a proof for execution.

        If the proof already exists, its ID is returned immediately. Otherwise,
        it's added to the database and a background task is created to run it.

        Args:
            proof: The LeanProof object to be executed.
            config: The configuration for the proof execution.

        Returns:
            A dictionary containing the unique ID of the proof.
        """
        tmp = await self.proof_database.proof_exists(proof=proof)
        if tmp:
            logger.info(f"Proof already submitted: {tmp}, returning existing proof ID")
            return {"id": tmp}
        await self.proof_database.insert_hash(proof=proof)
        task = asyncio.create_task(self.run_proof(proof=proof, config=config))
        logger.info(f"Submitted proof: {proof.proof_id}")
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        return {"id": proof.proof_id}

    async def run_proof(
        self, *, proof: LeanProof, config: LeanProofConfig
    ) -> LeanProofResult:
        """
        Executes a single Lean proof.

        This method acquires a semaphore lock before running the proof to control
        concurrency. It updates the proof's status in the database before and
        after execution. If the proof result already exists in the database,
        it skips execution and returns the stored result.

        Args:
            proof: The LeanProof object to execute.
            config: The configuration for the proof execution.

        Returns:
            The result of the proof execution.
        """
        tmp = await self.proof_database.proof_exists(proof=proof)
        if tmp is None:
            tmp = proof.proof_id
            await self.proof_database.insert_hash(proof=proof)
        if await self.proof_database.result_exists(proof_id=tmp):
            logger.info(f"Proof already exists in database: {tmp}, skipping execution")
            return await self.get_result(proof_id=tmp)
        await self.proof_database.update_status(
            proof_id=proof.proof_id, status=LeanProofStatus.PENDING
        )
        async with self.lean_semaphore:
            try:
                logger.info(f"Running proof: {proof}")
                logger.info(f"Config: {config}")
                await self.proof_database.update_status(
                    proof_id=proof.proof_id, status=LeanProofStatus.RUNNING
                )
                result = await proof.execute(config)
                logger.info(f"Proof result: {result}")
                await self.proof_database.insert_proof(
                    proof=proof, config=config, result=result
                )
                await self.proof_database.update_status(
                    proof_id=proof.proof_id, status=result.status
                )
                logger.info("Proof result inserted into database")
                return result
            except Exception as e:
                logger.error(f"Error running proof: {e}")
                await self.proof_database.update_status(
                    proof_id=proof.proof_id, status=LeanProofStatus.ERROR
                )
                return LeanProofResult(
                    status=LeanProofStatus.ERROR,
                    error_message=str(e),
                )

    async def get_result(self, proof_id: str) -> LeanProofResult:
        """
        Retrieves the result of a proof from the database.

        Args:
            proof_id: The unique identifier of the proof.

        Returns:
            The result of the proof.
        """
        return await self.proof_database.get_result(proof_id)
