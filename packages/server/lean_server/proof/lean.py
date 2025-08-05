import asyncio
import json
import logging

from ..config import CONFIG
from .proto import LeanProofConfig, LeanProofResult

logger = logging.getLogger(__name__)


class LeanProof:
    def __init__(self, *, proof: str):
        self.lean_code = proof

    async def execute(self, config: LeanProofConfig):
        try:
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

            try:
                result = json.loads(stdout.decode("utf-8"))
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {e}")
                result = {
                    "raw": stdout.decode("utf-8"),
                    "parse_error_message": str(e),
                }

            error_message = stderr.decode("utf-8") if stderr else None

            return LeanProofResult(result=result, error_message=error_message)
        except Exception as e:
            logger.error(f"Error executing proof: {e}")
            return LeanProofResult(error_message=str(e))
