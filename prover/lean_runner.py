import json
import subprocess


class Proof(object):
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
            ["/root/.elan/bin/lake", "exe", "repl"],
            input=self.command,
            capture_output=True,
            text=True,
            cwd="/root/playground",
        )
        return {
            "stdout": outputs.stdout,
            "stderr": outputs.stderr,
            "returncode": outputs.returncode,
        }


if __name__ == "__main__":
    with open("test.lean", "r") as f:
        code = f.read()
    proof = Proof(code)
    result = proof.execute()
    print("========== stdout ==========")
    print(result["stdout"])
    print("========== stderr ==========")
    print(result["stderr"])
    print("========== returncode ==========")
    print(result["returncode"])
