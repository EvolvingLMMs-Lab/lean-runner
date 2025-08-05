import asyncio
import logging
from pathlib import Path

from lean_client import AsyncLeanClient
from lean_client.proof.proto import Proof

logging.basicConfig(level=logging.INFO)


async def submit_async():
    async with AsyncLeanClient(base_url="http://0.0.0.0:8080", timeout=60.0) as client:
        result = await client.submit(proof=Path(__file__).parent / "test.lean")
    print(result)
    return result


async def get_result_async(result: Proof):
    async with AsyncLeanClient(base_url="http://0.0.0.0:8080", timeout=60.0) as client:
        result = await client.get_result(proof=result)
    return result


async def main():
    result = await submit_async()
    result = await get_result_async(result)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
