import json

from lean_client import LeanClient


def get_data(data: str, num: int) -> list[dict]:
    with open(data) as f:
        data = json.load(f)
    return [d["code"] for d in data[:num]], data[:num]


def main():
    data = "/mnt/raid10/pufanyi/lmms-lean-runner/demo/data/to_inference_codes.json"
    client = LeanClient("http://localhost:8080")
    codes, full_data = get_data(data, 10)
    results = client.verify_all(
        codes,
        max_workers=20,
        progress_bar=True,
        total=len(codes),
    )
    final_results = []
    for r, d in zip(results, full_data, strict=False):
        final_results.append(
            {
                "input": d,
                "result": r.model_dump_json(),
            }
        )
    with open("minif2f.json", "w") as f:
        json.dump(final_results, f)


if __name__ == "__main__":
    main()
