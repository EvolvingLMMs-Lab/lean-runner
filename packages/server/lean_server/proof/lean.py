"""
This module defines the LeanProof class for executing Lean proofs.
"""

import asyncio
import json
import logging

from ..config import Config
from ..utils.uuid.uuid import uuid
from .proto import LeanProofConfig, LeanProofResult, LeanProofStatus

logger = logging.getLogger(__name__)


class LeanProof:
    """
    Represents a Lean proof that can be executed.

    This class encapsulates the Lean code for a proof and provides a method
    to execute it as a subprocess. It handles communication with the Lean
    process, including timeouts and error handling.

    Attributes:
        lean_code (str): The Lean code of the proof.
        proof_id (str): A unique identifier for the proof.
        config (Config): The application configuration.
    """

    def __init__(self, *, proof_id: str | None = None, proof: str, config: Config):
        """
        Initializes a LeanProof instance.

        Args:
            proof_id: An optional unique identifier for the proof. If not
                provided, a new UUID will be generated.
            proof: The Lean code for the proof.
            config: The application configuration.
        """
        self.lean_code = proof
        if proof_id is None:
            self.proof_id = uuid()
        else:
            self.proof_id = proof_id
        self.config = config

    async def execute(self, config: LeanProofConfig) -> LeanProofResult:
        """
        Executes the Lean proof as a subprocess.

        This method runs the Lean executable, sends the proof code to it, and
        waits for the result. It handles timeouts, process errors, and JSON
        parsing of the output.

        Args:
            config: The configuration for this specific proof execution.

        Returns:
            A LeanProofResult object containing the status and result of the
            proof execution.
        """
        proc = None
        try:
            command = {
                "cmd": self.lean_code,
                "allTactics": config.all_tactics,
                "ast": config.ast,
                "tactics": config.tactics,
                "premises": config.premises,
            }
            logger.info(f"Executing command: {command}")

            # Create subprocess with proper resource management
            proc = await asyncio.create_subprocess_exec(
                self.config.lean.executable,
                "exe",
                "repl",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.config.lean.workspace,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(input=json.dumps(command).encode("utf-8")),
                    timeout=config.timeout,
                )
            except TimeoutError:
                logger.error(f"Lean process timed out after {config.timeout} seconds")
                # Forcefully terminate the process
                if proc.returncode is None:
                    proc.terminate()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=5.0)
                    except TimeoutError:
                        logger.warning("Force killing Lean process")
                        proc.kill()
                        await proc.wait()

                return LeanProofResult(
                    status=LeanProofStatus.ERROR,
                    error_message=f"Process timed out after {config.timeout} seconds",
                    result={"status": "timeout"},
                )

            # Check process return code
            if proc.returncode != 0:
                logger.warning(f"Lean process exited with code {proc.returncode}")
                error_msg = (
                    stderr.decode("utf-8")
                    if stderr
                    else f"Process exited with code {proc.returncode}"
                )
                return LeanProofResult(
                    status=LeanProofStatus.ERROR,
                    error_message=error_msg,
                    result={"status": "process_error", "return_code": proc.returncode},
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
            logger.error(f"Error executing proof: {e}", exc_info=True)
            # Ensure process cleanup in case of unexpected errors
            if proc and proc.returncode is None:
                try:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), timeout=5.0)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup process: {cleanup_error}")
                    try:
                        proc.kill()
                        await proc.wait()
                    except Exception:
                        pass  # Best effort cleanup

            return LeanProofResult(
                status=LeanProofStatus.ERROR,
                error_message=str(e),
                result={"status": "failed", "error_type": type(e).__name__},
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

        This method filters out warning messages if requested and determines
        the overall success of the proof based on the presence of errors.

        Args:
            result: The original result dictionary from Lean.
            hide_warnings: If True, removes all messages with
                severity 'warning'.

        Returns:
            A tuple containing the processed result dictionary and a boolean
            indicating success.
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
