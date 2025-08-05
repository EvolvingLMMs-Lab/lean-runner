# Lean Client

A Python client for the Lean Server API.

This package provides a simple, asynchronous `LeanClient` to interact with the `lean-server`.

## 📦 Installation

### As a Standalone Package
To install this package from PyPI (once published):
```bash
pip install lean-client
```

### For Development
This package is part of a monorepo. For development, follow the setup instructions in the [root README](../../README.md). The recommended installation command within the dev container is:
```bash
# This installs the client in editable mode
uv pip install -e .
```

## 🚀 Usage

The client is asynchronous and designed to be used with `asyncio`.

Here is a basic usage example:

```python
import asyncio
from client import LeanClient

async def main():
    # Assumes the server is running on http://localhost:8000
    # The client can be used as an async context manager.
    async with LeanClient("http://localhost:8000") as client:
        proof_to_check = "def my_theorem : 1 + 1 = 2 := rfl"

        # Optional configuration can be passed as a dictionary.
        config = {"timeout": 60}

        print(f"Checking proof: '{proof_to_check}'")
        result = await client.check_proof(proof_to_check, config=config)

        print("\nServer response:")
        print(result)

if __name__ == "__main__":
    # To run the example, save it as a file (e.g., `test_client.py`)
    # and run `python test_client.py` in a terminal where the server is running.
    asyncio.run(main())
```
