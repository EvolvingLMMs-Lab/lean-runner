import asyncio
import json
import logging

from ..config import Config
from ..utils.uuid.uuid import uuid
from .proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class LeanProof:
    def __init__(self, *, proof_id: str | None = None, proof: str, config: Config):
        self.lean_code = proof
        if proof_id is None:
            self.proof_id = uuid()
        else:
            self.proof_id = proof_id
        self.config = config

    async def execute(self, config: LeanProofConfig) -> LeanProofResult:
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
                self.config.lean.executable,
                "exe",
                "repl",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.config.lean.workspace,
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

            result, success = self._handle_result(
                result=result,
                hide_warnings=True,
            )
            return LeanProofResult(
                success=success,
                status=status,
                result=result,
                error_message=error_message,
            )
        except Exception as e:
            logger.error(f"Error executing proof: {e}")
            return LeanProofResult(
                status=LeanProofStatus.ERROR,
                error_message=str(e),
                result={"status": "failed"},
            )

    def _has_error(self, result: dict) -> bool:
        """Check if a proof result has any error messages."""
        if result and "messages" in result:
            for msg in result["messages"]:
                if msg.get("severity") == "error":
                    return True
        return False

    def _handle_result(
        self, result: dict, hide_warnings: bool = True
    ) -> tuple[dict, bool]:
        """
        Process the result dictionary returned from Lean.

        Args:
            result (dict): The original result dictionary.
            hide_warnings (bool): If True,
                removes all messages with severity == 'warning'.

        Returns:
            dict: The processed result dictionary.
        """
        success = True
        final_result_messages = []
        if hide_warnings and "messages" in result:
            for msg in result["messages"]:
                if msg.get("severity") == "error":
                    success = False
                elif msg.get("severity") == "warning":
                    if hide_warnings:
                        continue
                final_result_messages.append(msg)
        result["messages"] = final_result_messages

        return result, success
