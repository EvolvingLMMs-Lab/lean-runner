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

## Batch Verification of Multiple Proofs

For verifying a large number of proofs, the `verify_all` method provides a high-performance, memory-efficient solution. It processes proofs concurrently and yields results as they become available, making it ideal for handling large datasets or streaming data.

### Synchronous: `verify_all`

The synchronous `verify_all` method uses a thread pool to verify proofs from any iterable (like a list or a generator) concurrently.

**Features:**
- **Concurrent**: Uses `concurrent.futures.ThreadPoolExecutor` to run multiple verification tasks in parallel.
- **Memory-Efficient**: Processes proofs as an iterator, without loading the entire dataset into memory.
- **Progress Bar**: Displays a `tqdm` progress bar to track progress.

**Example (`demo/verify_all_sync_iterator.py`):**
```python
from pathlib import Path
from lean_client import LeanClient

# A generator to simulate a streaming data source
def proof_generator():
    lean_files = (Path(__file__).parent).glob("*.lean")
    for file_path in lean_files:
        yield file_path

def main():
    with LeanClient(base_url="http://0.0.0.0:8080") as client:
        # Pass the generator directly to the function
        results_iterator = client.verify_all(
            proofs=proof_generator(),
            max_workers=4,  # Limit concurrent requests
        )

        print("\n--- Verification Results ---")
        for result in results_iterator:
            print(result)

if __name__ == "__main__":
    main()
```

### Asynchronous: `aio.verify_all`

The asynchronous version, `client.aio.verify_all`, is even more powerful. It uses an `asyncio` producer-consumer model to handle proofs from either a standard iterable or an asynchronous iterable.

**Features:**
- **Highly Concurrent**: Manages concurrency with `asyncio` tasks, ideal for I/O-bound operations.
- **Back-pressure Management**: Uses a bounded queue to prevent the data source from overwhelming the system, ensuring stable memory usage.
- **Flexible Inputs**: Accepts both synchronous (`Iterable`) and asynchronous (`AsyncIterable`) sources of proofs.

**Example (`demo/verify_all_async_iterator.py`):**
```python
import asyncio
from pathlib import Path
from collections.abc import AsyncIterable
from lean_client import AsyncLeanClient

# An async generator to simulate a streaming data source
async def proof_generator() -> AsyncIterable[Path]:
    lean_files = (Path(__file__).parent).glob("*.lean")
    for file_path in lean_files:
        await asyncio.sleep(0.1) # Simulate I/O delay
        yield file_path

async def main():
    async with AsyncLeanClient(base_url="http://0.0.0.0:8080") as client:
        # Pass the async generator directly to the function
        results_iterator = client.verify_all(
            proofs=proof_generator(),
            max_workers=4,
        )

        print("\n--- Verification Results ---")
        async for result in results_iterator:
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
- **`verify_all(proofs, config, max_workers, progress_bar, total)`**: Verifies a collection of proofs concurrently. Returns an iterator that yields results as they complete.
- **`submit(proof, config)`**: Submits a proof for background processing. Returns a `Proof` object with an ID.
- **`get_result(proof)`**: Retrieves the result of a previously submitted proof.
- **`close()`**: Closes the underlying HTTP session. The client can also be used as a context manager (`with LeanClient(...) as client:`), which handles closing automatically.
