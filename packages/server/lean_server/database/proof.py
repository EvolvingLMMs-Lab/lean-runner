import logging

import aiosqlite

from ..config import CONFIG
from ..proof.lean import LeanProof
from ..proof.proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class ProofDatabase:
    def __init__(self):
        self.sql_path = CONFIG.sqlite.database_path
        self.timeout = CONFIG.sqlite.timeout

    async def create_table(self):
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
            await db.commit()

    async def update_status(self, *, proof_id: str, status: LeanProofStatus):
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
