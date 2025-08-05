import asyncio
import json
import logging

from ..config import CONFIG
from ..utils.uuid.uuid import uuid
from .proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class LeanProof:
    def __init__(self, *, proof_id: str | None = None, proof: str):
        self.lean_code = proof
        if proof_id is None:
            self.proof_id = uuid()
        else:
            self.proof_id = proof_id

    async def execute(
        self, config: LeanProofConfig, proof_database
    ) -> LeanProofResult:
        try:
            await proof_database.update_status(
                proof_id=self.proof_id, status=LeanProofStatus.RUNNING
            )

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

            error_message = stderr.decode("utf-8") if stderr else None

            try:
                result = json.loads(stdout.decode("utf-8"))
                status = LeanProofStatus.FINISHED
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {e}")
                result = {
                    "raw": stdout.decode("utf-8"),
                    "parse_error_message": str(e),
                }
                status = LeanProofStatus.ERROR

            await proof_database.update_status(proof_id=self.proof_id, status=status)

            return LeanProofResult(
                status=status,
                result=result,
                error_message=error_message,
            )
        except Exception as e:
            logger.error(f"Error executing proof: {e}")
            await proof_database.update_status(
                proof_id=self.proof_id, status=LeanProofStatus.ERROR
            )
            return LeanProofResult(status=LeanProofStatus.ERROR, error_message=str(e))
