import aiosqlite

from lean_server.config import CONFIG


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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    async def insert_proof(self, proof: str):
        async with aiosqlite.connect(self.sql_path, timeout=self.timeout) as db:
            await db.execute("INSERT INTO proof (proof) VALUES (?)", (proof,))
            await db.commit()
