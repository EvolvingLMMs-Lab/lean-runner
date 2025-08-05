import asyncio
import logging
from pathlib import Path

from lean_client import AsyncLeanClient, LeanClient

logging.basicConfig(level=logging.INFO)


def check():
    with LeanClient(base_url="http://0.0.0.0:8000") as client:
        result = client.verify(
            proof=Path(__file__).parent / "test.lean",
            config={
                "timeout": 30,
            },
        )
        print(result)


async def check_async():
    async with AsyncLeanClient(base_url="http://0.0.0.0:8000", timeout=60.0) as client:
        result = await client.verify(
            proof=Path(__file__).parent / "test.lean",
            config={
                "timeout": 30,
            },
        )
        print(result)


async def main():
    # Test synchronous version
    print("=== Testing Synchronous Version ===")
    check()

    # Test asynchronous concurrent version
    print("\n=== Testing Asynchronous Concurrent Version ===")
    tasks = [check_async() for _ in range(10)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
