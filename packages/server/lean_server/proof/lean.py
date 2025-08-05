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
                
                # check if error in message
                print("checking error")
                if self._has_error(result):
                    raise Exception(error_message)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {e}")
                result = {
                    "raw": stdout.decode("utf-8"),
                    "parse_error_message": str(e),
                }
                status = LeanProofStatus.ERROR
                
            # process result
            result['status'] = 'success'
            result = self._handle_result(
                result=result,
                hide_warnings=True  # to replace with a config boolean
            )
            return LeanProofResult(
                status=status,
                result=result,
                error_message=error_message,
            )
        except Exception as e:
            logger.error(f"Error executing proof: {e}")
            return LeanProofResult(status=LeanProofStatus.ERROR, error_message=str(e), result={'status': "failed"})

    def _has_error(self, result: dict) -> bool:
        """Check if a proof result has any error messages."""
        if result and "messages" in result:
            for msg in result["messages"]:
                if msg.get("severity") == "error":
                    return True
        return False
    
    def _handle_result(self, result: dict, hide_warnings: bool = True) -> dict:
        """
        Process the result dictionary returned from Lean.
        
        Args:
            result (dict): The original result dictionary.
            hide_warnings (bool): If True, removes all messages with severity == 'warning'.
        
        Returns:
            dict: The processed result dictionary.
        """
        if hide_warnings and "messages" in result:
            result["messages"] = [
                msg for msg in result["messages"]
                if msg.get("severity") != "warning"
            ]
        
        return result