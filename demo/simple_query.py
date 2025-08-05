from pathlib import Path
import logging
from lean_client import LeanClient, AsyncLeanClient

import asyncio

logging.basicConfig(level=logging.INFO)

def check():
    with LeanClient(base_url="http://0.0.0.0:8000") as client:
        result = client.check_proof(
            proof=Path(__file__).parent / "test.lean",
            config={
                "timeout": 30,
            },
        )
        print(result)

async def check_async():
    async with AsyncLeanClient(base_url="http://0.0.0.0:8000") as client:
        result = await client.check_proof(
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
    
        