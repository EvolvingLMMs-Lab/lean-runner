import json
import logging
import subprocess

from lean_server.config import CONFIG

logger = logging.getLogger(__name__)


class LeanProof:
    def __init__(self, proof: str):
        self.proof = proof
        self.lean_workspace = "playground"
        self.command = json.dumps(
            {
                "cmd": self.proof,
                "allTactics": False,
                "ast": False,
                "tactics": False,
                "premises": False,
            }
        )

    def execute(self):
        outputs = subprocess.run(
            [CONFIG.lean.executable, "exe", "repl"],
            input=self.command,
            capture_output=True,
            text=True,
            cwd=CONFIG.lean.workspace,
        )
        return {
            "stdout": outputs.stdout,
            "stderr": outputs.stderr,
            "returncode": outputs.returncode,
        }


if __name__ == "__main__":
    with open("test.lean") as f:
        code = f.read()
    proof = LeanProof(code)
    result = proof.execute()
    logger.info(result)
    logger.info(result["stdout"])
    logger.info(result["stderr"])
    logger.info(result["returncode"])
