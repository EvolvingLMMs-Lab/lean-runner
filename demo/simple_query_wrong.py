import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from lean_runner import AsyncLeanClient, LeanClient

logging.basicConfig(level=logging.INFO)


HOST = "localhost:50051"


def check():
    with LeanClient(address=HOST) as client:
        result = client.verify(proof=Path(__file__).parent / "test4.lean")
        print(result)


async def check_async():
    async with AsyncLeanClient(address=HOST) as client:
        result = await client.verify(proof=Path(__file__).parent / "test4.lean")
        print(result)


async def main():
    # Test synchronous version
    print("=== Testing Synchronous Version ===")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(10):
            executor.submit(check)

    # Test asynchronous concurrent version
    print("\n=== Testing Asynchronous Concurrent Version ===")
    tasks = [check_async() for _ in range(5)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
