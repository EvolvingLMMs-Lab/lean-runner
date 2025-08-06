import asyncio
from collections.abc import Iterable

import datasets
from lean_client import LeanClient
from lean_client.proof.proto import LeanProofStatus


def get_data(data: datasets.Dataset) -> Iterable[str]:
    for d in data:
        yield d["full_code"][0]


async def main():
    data = datasets.load_dataset("pufanyi/miniF2F-code-compilation")["train"]
    client = LeanClient("http://localhost:8080")
    results = client.aio.verify_all(
        get_data(data),
        max_workers=32,
        progress_bar=True,
        total=len(data),
    )
    result = 0
    error_num = 0
    num = 0
    async for r in results:
        if r.success:
            result += 1
        if r.status != LeanProofStatus.FINISHED:
            error_num += 1
        num += 1
    print(result)
    print(num)


if __name__ == "__main__":
    asyncio.run(main())
