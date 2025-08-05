import asyncio
import datasets
from typing import Iterable
from lean_client import AsyncLeanClient


def get_data() -> Iterable[str]:
    data = datasets.load_dataset("pufanyi/miniF2F-code-compilation")["train"]
    for d in data:
        yield d["full_code"][0]
        break

async def main():
    client = AsyncLeanClient("http://localhost:8080")
    results = client.verify_all(
        data,
        max_workers=32,
        progress_bar=True,
    )
    async for r in results:
        print(r)

if __name__ == "__main__":
    data = get_data()
    asyncio.run(main())