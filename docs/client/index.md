# Lean Client Documentation

This document provides instructions and examples on how to use the `lean-client` Python library to interact with the Lean Server. The client supports both synchronous and asynchronous operations, allowing for flexibility in different use cases.

## Installation

### 📦 Install from PyPI (Recommended)

You can install the client directly from PyPI:

```bash
pip install lmms-lean-client
```

## Quick Start: Verifying a Proof

The quickest way to check a Lean proof is to use the `verify` method. This sends the proof to the server and waits for the result in a single blocking call.

### Synchronous Verification

This is the simplest way to use the client. The `verify` method sends the proof and waits for the server's response.

```python
from pathlib import Path
from lean_client import LeanClient  # Import client

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

For non-blocking operations, you can use the `AsyncLeanClient`. This is useful in applications that handle many I/O operations concurrently.

```python
import asyncio
from pathlib import Path
from lean_client import AsyncLeanClient  # Import the async client

# Define the main asynchronous function
async def main():
    # Create an asynchronous context with the Lean client
    async with AsyncLeanClient(base_url="http://0.0.0.0:8080") as client:
        # Define the path to the Lean proof file
        proof_file = Path(__file__).parent / "test1.lean"

        # Submit the proof file for verification asynchronously
        result = await client.verify(proof=proof_file)

        # Print the verification result
        print(result)

# Run the async main function using asyncio
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

```python
from pathlib import Path
from lean_client import LeanClient  # Import client

# A generator to simulate a streaming data source
def proof_generator():
    lean_files = (Path(__file__).parent).glob("*.lean")
    for file_path in lean_files:
        yield file_path

def main():
    with LeanClient(base_url="http://0.0.0.0:8080") as client:
        # Pass the generator directly to the function
        # Uses ThreadPoolExecutor under the hood
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

### Asynchronous: `verify_all`

The asynchronous version, `AsyncLeanClient.verify_all`, is even more powerful. It uses an `asyncio` producer-consumer model to handle proofs from either a standard iterable or an asynchronous iterable.

**Features:**

- **Highly Concurrent**: Manages concurrency with `asyncio` tasks, ideal for I/O-bound operations.
- **Back-pressure Management**: Uses a bounded queue to prevent the data source from overwhelming the system, ensuring stable memory usage.
- **Flexible Inputs**: Accepts both synchronous (`Iterable`) and asynchronous (`AsyncIterable`) sources of proofs.

```python
import asyncio
from pathlib import Path
from collections.abc import AsyncIterable
from lean_client import AsyncLeanClient  # Import async client

# An async generator to simulate a streaming data source
async def proof_generator() -> AsyncIterable[Path]:
    lean_files = (Path(__file__).parent).glob("*.lean")
    for file_path in lean_files:
        await asyncio.sleep(0.1) # Simulate I/O delay
        yield file_path

async def main():
    async with AsyncLeanClient(base_url="http://0.0.0.0:8080") as client:
        # Pass the async generator directly to the function
        # Uses AsyncIO under the hood
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
import time
from pathlib import Path
from lean_client import LeanClient
from rich.console import Console

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
            # Update UI here...
            time.sleep(1)  # Poll every 1 seconds

# ... (UI code and main execution)
```

### Asynchronous Polling Example

The asynchronous version is more efficient for handling multiple concurrent requests, as it uses `asyncio.gather` to submit and poll for proofs in parallel.

```python
import asyncio
from pathlib import Path
from lean_client import AsyncLeanClient  # Import async client

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
            # Process results and update UI here...

            pending_proofs = newly_pending
            await asyncio.sleep(1)  # Poll every 1 seconds

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

---

### `AsyncLeanClient(base_url, timeout)`

- **`base_url`**: The base URL of the Lean Server (e.g., http://localhost:8080).

- **`timeout`**: Timeout for HTTP requests in seconds.

This client is designed for use with asyncio and supports concurrent verification of proofs using asynchronous queues and tasks.

### Methods

- **`await submit(proof, config)`**:
  Submits a proof for background processing via /prove/submit.
  Returns a Proof object with a unique ID.

- **`await verify(proof, config)`**:
  Sends a proof for immediate verification via /prove/check.
  Returns a ProofResult with the verification status and any messages.

- **`verify_all(proofs, config, max_workers, progress_bar, total)`**:
  Verifies a collection of proofs concurrently using an asyncio-based producer-consumer model.
  Returns an async iterator that yields ProofResult objects as they complete.
  Accepts both Iterable and AsyncIterable sources.

- **`await get_result(proof)`**:
  Retrieves the verification result of a previously submitted Proof.

- **`await close()`**:
  Closes the underlying httpx.AsyncClient session.
  The client can also be used with an async context manager - `async with AsyncLeanClient(...) as client:`
