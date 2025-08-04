import asyncio
import json
import logging

from lean_server.config import CONFIG

from .config import LeanProofConfig

logger = logging.getLogger(__name__)


class LeanProof:
    def __init__(self, proof: str):
        self.proof = proof
        self.lean_workspace = "playground"

    async def execute(self, config: LeanProofConfig):
        command = {
            "cmd": self.proof,
            "allTactics": config.all_tactics,
            "ast": config.ast,
            "tactics": config.tactics,
            "premises": config.premises,
        }
        logger.info(f"Executing command: {command}")
        outputs = await asyncio.subprocess.create_subprocess_exec(
            [CONFIG.lean.executable, "exe", "repl"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            cwd=CONFIG.lean.workspace,
        )
        return {
            "stdout": outputs.stdout,
            "stderr": outputs.stderr,
            "returncode": outputs.returncode,
        }
