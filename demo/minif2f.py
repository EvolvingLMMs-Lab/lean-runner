import json

from lean_client import LeanClient
from lean_client.proof.proto import LeanProofStatus


def get_data(data: str) -> list[dict]:
    with open(data) as f:
        data = json.load(f)
    return [d["code"] for d in data]


def main():
    data = "data/miniF2F-code-compilation.json"
    client = LeanClient("http://localhost:8888")
    results = client.verify_all(
        get_data(data),
        max_workers=32,
        progress_bar=True,
        total=len(data),
    )
    result = 0
    error_num = 0
    num = 0
    for r in results:
        if r.success:
            result += 1
        if r.status != LeanProofStatus.FINISHED:
            error_num += 1
        num += 1
    print(result)
    print(num)


if __name__ == "__main__":
    main()
