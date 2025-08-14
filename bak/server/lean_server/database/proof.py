"""
This module provides a database interface for storing and managing Lean proofs.
"""

import asyncio
import logging
from collections.abc import AsyncIterator

import aiosqlite
import xxhash

from ..proof.lean import LeanProof
from ..proof.proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class ProofDatabase:
    """
    Handles all database operations related to Lean proofs.

    This class manages an SQLite database to store proof information, including
    the proof code, configuration, results, and status. It uses `aiosqlite`
    for asynchronous database access.

    Attributes:
        sql_path (str): The file path to the SQLite database.
        timeout (int): The timeout in seconds for database connections.
    """

    def __init__(self, database_path: str, timeout: int):
        """
        Initializes the ProofDatabase.

        Args:
            database_path: The path to the SQLite database file.
            timeout: The connection timeout in seconds.
        """
        self.sql_path = database_path
        self.timeout = timeout

    async def create_table(self):
        """
        Creates the necessary tables in the database if they don't already exist.
        """
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS proof (
                    id TEXT PRIMARY KEY,
                    proof TEXT,
                    config TEXT,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS status (
                    id TEXT PRIMARY KEY,
                    status TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS hash (
                    id TEXT PRIMARY KEY,
                    proof TEXT,
                    value TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_value_hash ON hash (value)
                """
            )
            await db.commit()

    @staticmethod
    async def calc_proof_hash(lean_code: str) -> str:
        """
        Calculates the xxhash 64-bit hash of the Lean code.

        Args:
            lean_code: The Lean code to hash.

        Returns:
            The hex digest of the hash.
        """
        return xxhash.xxh64(lean_code).hexdigest()

    async def proof_exists(self, *, proof: LeanProof) -> str | None:
        """
        Checks if a proof with the same code already exists in the database.

        Args:
            proof: The LeanProof object.

        Returns:
            The ID of the existing proof if found, otherwise None.
        """
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            tmp = await self.calc_proof_hash(proof.lean_code)
            cursor = await db.execute(
                "SELECT id, proof FROM hash WHERE value = ?",
                (tmp,),
            )
            async for row in cursor:
                if row[1] == proof.lean_code:
                    return row[0]
            return None

    async def insert_hash(self, *, proof: LeanProof) -> None:
        """
        Inserts the hash of a proof's code into the 'hash' table.

        Args:
            proof: The LeanProof object.
        """
        tmp = await self.calc_proof_hash(proof.lean_code)
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute(
                "INSERT OR REPLACE INTO hash (id, proof, value) VALUES (?, ?, ?)",
                (proof.proof_id, proof.lean_code, tmp),
            )
            await db.commit()

    async def result_exists(self, *, proof_id: str) -> bool:
        """
        Checks if a result for a given proof ID exists in the 'proof' table.

        Args:
            proof_id: The ID of the proof.

        Returns:
            True if the result exists, False otherwise.
        """
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            cursor = await db.execute(
                "SELECT 1 FROM proof WHERE id = ?",
                (proof_id,),
            )
            row = await cursor.fetchone()
            return row is not None

    async def update_status(self, *, proof_id: str, status: LeanProofStatus):
        """
        Updates the status of a proof in the 'status' table.

        Args:
            proof_id: The ID of the proof.
            status: The new status of the proof.
        """
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute(
                "INSERT OR REPLACE INTO status (id, status) VALUES (?, ?)",
                (proof_id, status.value),
            )
            await db.commit()

    async def insert_proof(
        self,
        *,
        proof: LeanProof,
        config: LeanProofConfig,
        result: LeanProofResult,
    ) -> str:
        """
        Inserts a completed proof's data into the 'proof' table.

        Args:
            proof: The LeanProof object.
            config: The configuration used for the proof.
            result: The result of the proof execution.

        Returns:
            The ID of the inserted proof.
        """
        config_string = config.model_dump_json()
        result_string = result.model_dump_json()
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute(
                "INSERT INTO proof (id, proof, config, result) VALUES (?, ?, ?, ?)",
                (proof.proof_id, proof.lean_code, config_string, result_string),
            )
            await db.commit()
            return proof.proof_id

    async def get_result(self, proof_id: str) -> LeanProofResult:
        """
        Retrieves the result of a proof from the database.

        It first checks the status and then retrieves the full result if
        the proof is finished or has an error.

        Args:
            proof_id: The ID of the proof.

        Returns:
            A LeanProofResult object.
        """
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            cursor = await db.execute(
                "SELECT status FROM status WHERE id = ?",
                (proof_id,),
            )
            status_query_result = await cursor.fetchone()
            if status_query_result is None:
                return LeanProofResult(status=LeanProofStatus.PENDING)
            status = LeanProofStatus(status_query_result[0])
            if status == LeanProofStatus.FINISHED or status == LeanProofStatus.ERROR:
                cursor = await db.execute(
                    "SELECT result FROM proof WHERE id = ?",
                    (proof_id,),
                )
                result = await cursor.fetchone()
                if result is None:
                    return LeanProofResult(status=status)
                return LeanProofResult.model_validate_json(result[0])
            else:
                return LeanProofResult(status=status)

    async def clean_db(self, *, seconds: int = 0):
        """
        Clean the database by removing old records older than 24 hours.
        """
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            # Remove old proof records (older than 24 hours)
            await db.execute(
                "DELETE FROM proof WHERE created_at < datetime('now', '-1 day')"
            )

            # Remove orphaned status entries (status entries without corresponding
            # proof records)
            await db.execute(
                "DELETE FROM status WHERE id NOT IN (SELECT id FROM proof)"
            )

            await db.commit()
            logger.info("Database cleaned: removed old records older than 24 hours")

    async def fetch(self, query: str, batch_size: int = 100) -> AsyncIterator[dict]:
        """
        Fetch data from the database using a Producer/Consumer pattern for efficient
        batch processing.

        Args:
            query: SQL query string to execute
            batch_size: Number of rows to fetch per batch

        Yields:
            dict: Each row as a dictionary with column names as keys
        """
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        # Create a queue for producer-consumer pattern
        queue: asyncio.Queue[dict | None] = asyncio.Queue(maxsize=batch_size * 2)
        producer_finished = asyncio.Event()

        async def producer():
            """Producer coroutine that fetches data from database and puts
            it in queue"""
            try:
                async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
                    # Enable row factory to get dict-like results
                    db.row_factory = aiosqlite.Row

                    cursor = await db.execute(query)

                    while True:
                        # Fetch a batch of rows
                        rows = await cursor.fetchmany(batch_size)
                        if not rows:
                            break

                        # Put each row in the queue
                        for row in rows:
                            # Convert aiosqlite.Row to dict
                            row_dict = dict(row)
                            await queue.put(row_dict)

                    # Signal end of data
                    await queue.put(None)

            except Exception as e:
                logger.error(f"Error in fetch producer: {e}")
                # Put None to signal error/end to consumer
                try:
                    await queue.put(None)
                except Exception as e:
                    logger.error(f"Error putting None to queue: {e}")
                raise
            finally:
                producer_finished.set()

        # Start the producer task
        producer_task = asyncio.create_task(producer())

        try:
            # Consumer: yield items from the queue
            while True:
                try:
                    # Wait for item with timeout to avoid hanging
                    item = await asyncio.wait_for(queue.get(), timeout=self.timeout)

                    if item is None:
                        # End of data signal
                        break

                    yield item
                    queue.task_done()

                except TimeoutError:
                    logger.warning("Timeout waiting for data in fetch operation")
                    break
                except Exception as e:
                    logger.error(f"Error in fetch consumer: {e}")
                    break

        finally:
            # Cleanup: cancel producer if still running
            if not producer_task.done():
                producer_task.cancel()
                try:
                    await producer_task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error cancelling producer task: {e}")

            # Wait for producer to finish if it's still running
            try:
                await asyncio.wait_for(producer_finished.wait(), timeout=5.0)
            except TimeoutError:
                logger.warning("Producer did not finish within timeout")
