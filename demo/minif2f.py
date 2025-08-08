import json
from pathlib import Path

from lean_client import LeanClient
from lean_client.proof.proto import LeanProofStatus


def get_data(data_path: str) -> list[dict]:
    with open(data_path) as f:
        data = json.load(f)
    return [d["code"] for d in data]


def main():
    data_path = Path(__file__).parent / "data" / "to_inference_codes.json"
    data = get_data(data_path)
    client = LeanClient("http://localhost:8080")
    results = client.verify_all(
        data,
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
    # print(result)
    # print(num)


if __name__ == "__main__":
    main()
