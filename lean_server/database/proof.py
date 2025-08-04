import json

import aiosqlite

from lean_server.config import CONFIG
from lean_server.proof.lean import LeanProof
from lean_server.proof.config import LeanProofConfig


class ProofDatabase:
    def __init__(self):
        self.sql_path = CONFIG.sqlite.database_path
        self.timeout = CONFIG.sqlite.timeout

    async def create_table(self):
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS proof (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proof TEXT,
                    config TEXT,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    async def insert_proof(
        self, proof: LeanProof, config: LeanProofConfig, result: dict
    ) -> int:
        config_string = config.model_dump_json()
        result_string = json.dumps(result)
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            cursor = await db.execute(
                "INSERT INTO proof (proof, config, result) VALUES (?, ?, ?)",
                (proof.lean_code, config_string, result_string),
            )
            await db.commit()
            return cursor.lastrowid
