# Lean Client Documentation

This document provides instructions and examples on how to use the `lean-client` Python library to interact with the Lean Server. The client supports both synchronous and asynchronous operations, allowing for flexibility in different use cases.

## Installation

To install the client, navigate to the `packages/client` directory and install it using pip:

```bash
cd packages/client
pip install .
```

## Quick Start: Verifying a Proof

The quickest way to check a Lean proof is to use the `verify` method. This sends the proof to the server and waits for the result in a single blocking call.

### Synchronous Verification

This is the simplest way to use the client. The `verify` method sends the proof and waits for the server's response.

```python
# demo/simple_query.py
from pathlib import Path
from lean_client import LeanClient

# Initialize the client
with LeanClient(base_url="http://0.0.0.0:8080") as client:
    # Path to your .lean file
    proof_file = Path(__file__).parent / "test1.lean"
    
    # Send for verification
    result = client.verify(proof=proof_file)
    
    # Print the result
    print(result)
```

### Asynchronous Verification

For non-blocking operations, you can use the `aio` client. This is useful in applications that handle many I/O operations concurrently.

```python
# demo/simple_query.py (async part)
import asyncio
from pathlib import Path
from lean_client import AsyncLeanClient

async def main():
    async with AsyncLeanClient(base_url="http://0.0.0.0:8080") as client:
        proof_file = Path(__file__).parent / "test1.lean"
        result = await client.verify(proof=proof_file)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Long-Running Proofs: Submit and Poll

For proofs that may take a long time to complete, it's better to submit them first and then poll for the result. This avoids long-held HTTP connections.

- `submit()`: Submits the proof and immediately returns a `Proof` object with a unique ID.
- `get_result()`: Polls the server for the status and result of the proof using its ID.

### Synchronous Polling Example

This example submits multiple proofs and then polls for their results in a loop, updating a live table in the console.

```python
# demo/submit_query.py
import time
from pathlib import Path
from lean_client import LeanClient
from rich.console import Console
# ... (other rich imports and helper functions)

def main():
    """Submit multiple proofs and display their status in a live table."""
    demo_dir = Path(__file__).parent
    lean_files = [
        demo_dir / "test1.lean",
        demo_dir / "test2.lean",
        # ... more files
    ]

    with LeanClient(base_url="http://0.0.0.0:8080") as client:
        # 1. Submit all proofs
        submitted_proofs = [client.submit(proof=file) for file in lean_files]
        
        proof_map = {file.name: proof for file, proof in zip(lean_files, submitted_proofs)}
        
        # 2. Poll for results until all are finished
        pending_proofs = list(proof_map.items())
        while pending_proofs:
            newly_pending = []
            for filename, proof in pending_proofs:
                result = client.get_result(proof=proof)
                # Update status...
                if result.status not in {"FINISHED", "ERROR"}:
                    newly_pending.append((filename, proof))
            
            pending_proofs = newly_pending
            # Update UI...
            time.sleep(1)

# ... (UI code and main execution)
```

### Asynchronous Polling Example

The asynchronous version is more efficient for handling multiple concurrent requests, as it uses `asyncio.gather` to submit and poll for proofs in parallel.

```python
# demo/submit_query_async.py
import asyncio
from pathlib import Path
from lean_client import AsyncLeanClient
# ... (other rich imports and helper functions)

async def main():
    """Submit multiple proofs and display their status in a live table."""
    demo_dir = Path(__file__).parent
    lean_files = [
        demo_dir / "test1.lean",
        demo_dir / "test2.lean",
        # ... more files
    ]

    async with AsyncLeanClient(base_url="http://0.0.0.0:8080") as client:
        # 1. Submit all proofs concurrently
        submitted_proofs = await asyncio.gather(
            *[client.submit(proof=file) for file in lean_files]
        )

        proof_map = {file.name: proof for file, proof in zip(lean_files, submitted_proofs)}

        # 2. Poll for results concurrently
        pending_proofs = list(proof_map.items())
        while pending_proofs:
            tasks = [client.get_result(proof=p) for _, p in pending_proofs]
            query_results = await asyncio.gather(*tasks)
            
            newly_pending = []
            # Process results and update UI...
            
            pending_proofs = newly_pending
            await asyncio.sleep(1)

# ... (UI code and main execution)
```

## API Reference

### `LeanClient(base_url, timeout)`
- **`base_url`**: The base URL of the Lean Server (e.g., `http://localhost:8080`).
- **`timeout`**: The timeout for HTTP requests in seconds.
- **`.aio`**: An attribute that provides access to the `AsyncLeanClient`.

### Methods
- **`verify(proof, config)`**: Sends a proof for immediate verification. Blocks until the result is returned.
- **`submit(proof, config)`**: Submits a proof for background processing. Returns a `Proof` object with an ID.
- **`get_result(proof)`**: Retrieves the result of a previously submitted proof.
- **`close()`**: Closes the underlying HTTP session. The client can also be used as a context manager (`with LeanClient(...) as client:`), which handles closing automatically.
