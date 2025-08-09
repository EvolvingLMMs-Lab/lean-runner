import asyncio
from lean_runner import AsyncLeanClient

async def verify_proof():
    async with AsyncLeanClient(base_url="http://localhost:8000") as client:
        # Submit proof for processing
        proof_id = await client.submit(
            proof="theorem test : 2 + 2 = 4 := by norm_num"
        )


asyncio.run(verify_proof())