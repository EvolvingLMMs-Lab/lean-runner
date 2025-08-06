import asyncio
from collections.abc import AsyncIterable
from pathlib import Path

from lean_client import AsyncLeanClient

# --- Configuration ---
# Make sure the lean server is running and accessible at this address.
LEAN_SERVER_URL = "http://0.0.0.0:8080"

# Use the .lean files in the current directory as test data, and repeat
# them to simulate a large workload.
DEMO_DIR = Path(__file__).parent
BASE_LEAN_FILES = [
    DEMO_DIR / "test1.lean",
    DEMO_DIR / "test2.lean",
    DEMO_DIR / "test3.lean",
    DEMO_DIR / "test4.lean",
]
# Repeat the list to simulate a much larger number of proofs.
REPETITIONS = 100
LEAN_FILES = BASE_LEAN_FILES * REPETITIONS


async def proof_generator() -> AsyncIterable[Path]:
    """
    An asynchronous generator that yields proof file paths one by one.
    This simulates a streaming data source, like reading from a database
    or a message queue.
    """
    print("(Async generator started, will yield proofs one by one with a small delay)")
    for file_path in LEAN_FILES:
        # Simulate a small I/O delay, e.g., fetching a record from a database.
        await asyncio.sleep(0.1)
        yield file_path


async def main():
    """
    Demonstrates calling verify_all with an asynchronous iterator (an async generator).
    """
    print("--- Starting verification with an asynchronous iterator ---")
    if not LEAN_FILES:
        print("No .lean files found in the demo directory. Please add some.")
        return

    print(
        f"Found {len(LEAN_FILES)} .lean files to verify: {[f.name for f in LEAN_FILES]}"
    )

    # The client can be used as an async context manager.
    async with AsyncLeanClient(base_url=LEAN_SERVER_URL) as client:
        # We pass the async generator directly to the function.
        # The client will handle consuming from it concurrently.
        results_iterator = client.verify_all(
            proofs=proof_generator(),
            max_workers=32,  # Limit concurrent requests
            progress_bar=True,
            total=len(LEAN_FILES),
        )

        print("\n--- Verification Results ---")
        # Asynchronously iterate over the results as they are completed.
        async for result in results_iterator:
            print(result)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nVerification cancelled by user.")
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"\nAn error occurred: {e}")
