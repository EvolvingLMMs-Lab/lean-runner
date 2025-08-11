import asyncio
import json

from lean_runner import LeanClient
from lean_runner.proof.proto import LeanProofStatus


async def main():
    with open(
        "/mnt/raid10/pufanyi/lmms-lean-runner/demo/data/to_inference_codes.json"
    ) as f:
        data = json.load(f)
    # data = data[:100]
    client = LeanClient("http://localhost:8888")
    data_name = [d["name"] for d in data]
    data_code = [d["code"] for d in data]
    results = client.aio.verify_all(
        data_code,
        max_workers=256,
        progress_bar=True,
        total=len(data_code),
    )
    result = 0
    error_num = 0
    num = 0
    result_list = []
    async for r in results:
        if r.success:
            result += 1
        if r.status != LeanProofStatus.FINISHED:
            error_num += 1
        num += 1
        result_list.append(r.model_dump_json())
    print(result)
    print(num)
    print(error_num)
    final_result_list = [
        {"name": n, "result": r} for n, r in zip(data_name, result_list, strict=False)
    ]
    with open("minif2f_async.json", "w") as f:
        json.dump(final_result_list, f)


if __name__ == "__main__":
    asyncio.run(main())
