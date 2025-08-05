import asyncio
import os

import aiohttp


async def call_check_proof():
    url = "http://localhost:8000/prove/check"

    with open(os.path.join(os.path.dirname(__file__), "test1.lean")) as f:
        proof = f.read()

    form_data = {"proof": proof, "config": "{}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as resp:
            print("Status:", resp.status)
            response_json = await resp.json()
            print("Response:", response_json)


asyncio.run(call_check_proof())
