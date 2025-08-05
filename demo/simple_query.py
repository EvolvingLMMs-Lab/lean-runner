from pathlib import Path

from lean_client import LeanClient

client = LeanClient(base_url="http://localhost:8080")


async def main():
    async with client:
        result = await client.check_proof(
            proof=Path(__file__).parent / "test.lean",
            config={
                "timeout": 10,
            },
        )
        print(result)
