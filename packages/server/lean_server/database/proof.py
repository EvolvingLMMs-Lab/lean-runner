import aiosqlite

from ..config import CONFIG
from ..proof.proto import LeanProofConfig, LeanProofResult, LeanProofStatus
from ..proof.lean import LeanProof
from ..utils.uuid.uuid import uuid


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
        proof_id: str | None = None,
    ) -> str:
        config_string = config.model_dump_json()
        result_string = result.model_dump_json()
        if proof_id is None:
            proof_id = uuid()
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute(
                "INSERT INTO proof (id, proof, config, result) VALUES (?, ?, ?, ?)",
                (proof_id, proof.lean_code, config_string, result_string),
            )
            await db.commit()
            return proof_id

    async def get_result(self, proof_id: str) -> LeanProofResult:
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            cursor = await db.execute(
                "SELECT result FROM proof WHERE id = ?",
                (proof_id,),
            )
            result = await cursor.fetchone()
            return LeanProofResult.model_validate_json(result)
