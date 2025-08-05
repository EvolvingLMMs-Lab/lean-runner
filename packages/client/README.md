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

### Basic Usage

Here is a basic usage example:

```python
import asyncio
from lean_client import LeanClient

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

### File Support

The client supports multiple ways to provide proof content:

1. **String content directly**:
```python
proof_content = "theorem test : 1 + 1 = 2 := by rfl"
result = await client.check_proof(proof_content)
```

2. **File path as string**:
```python
result = await client.check_proof("path/to/proof.lean")
```

3. **Path object**:
```python
from pathlib import Path
proof_file = Path("path/to/proof.lean")
result = await client.check_proof(proof_file)
```

### Complete Example with File

```python
import asyncio
from pathlib import Path
from lean_client import LeanClient

async def check_proof_from_file():
    async with LeanClient("http://localhost:8000") as client:
        # Create a test Lean file
        proof_file = Path("test_proof.lean")
        proof_content = """
theorem test_theorem : 1 + 1 = 2 := by
  rw [add_comm]
  rw [add_zero]
  rfl
"""
        
        # Write content to file
        with open(proof_file, 'w', encoding='utf-8') as f:
            f.write(proof_content)
        
        try:
            # Check proof from file
            result = await client.check_proof(proof_file, config={"timeout": 30})
            print(f"Proof check result: {result}")
        finally:
            # Clean up
            if proof_file.exists():
                proof_file.unlink()

if __name__ == "__main__":
    asyncio.run(check_proof_from_file())
```

## 📚 API Reference

### LeanClient

The main client class for interacting with the Lean Server.

#### `__init__(base_url: str)`
Initialize the client with the server's base URL.

#### `async check_proof(proof: Union[str, Path, os.PathLike], config: dict[str, Any] | None = None) -> dict[str, Any]`
Send a proof to the server for checking.

**Parameters:**
- `proof`: The proof content. Can be:
  - A string containing the proof
  - A Path object pointing to a file containing the proof
  - A string path to a file containing the proof
- `config`: Optional configuration dictionary for the proof check

**Returns:**
- A dictionary containing the server's response

#### `async close()`
Close the client session.

#### `async __aenter__()` and `async __aexit__()`
Async context manager support for automatic session management.
