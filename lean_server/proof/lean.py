import asyncio
import json
import logging

from lean_server.config import CONFIG

from .config import LeanProofConfig

logger = logging.getLogger(__name__)


class LeanProof:
    def __init__(self, *, proof: str):
        self.lean_code = proof

    async def execute(self, config: LeanProofConfig):
        command = {
            "cmd": self.lean_code,
            "allTactics": config.all_tactics,
            "ast": config.ast,
            "tactics": config.tactics,
            "premises": config.premises,
        }
        logger.info(f"Executing command: {command}")

        proc = await asyncio.create_subprocess_exec(
            CONFIG.lean.executable,
            "exe",
            "repl",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=CONFIG.lean.workspace,
        )

        stdout, stderr = await proc.communicate(
            input=json.dumps(command).encode("utf-8")
        )

        return {
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else "",
            "returncode": proc.returncode,
        }
