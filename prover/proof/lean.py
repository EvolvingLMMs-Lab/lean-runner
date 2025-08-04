import json
import subprocess

from prover.config import CONFIG

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
    print(result)
    print(result["stdout"])
    print(result["stderr"])
    print(result["returncode"])
