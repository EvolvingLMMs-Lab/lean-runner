import asyncio
from pathlib import Path
from lean_client.client.aio import AsyncLeanClient

# --- Configuration ---
# Make sure the lean server is running and accessible at this address.
LEAN_SERVER_URL = "http://127.0.0.1:8080"

# Use the .lean files in the current directory as test data, and repeat them to simulate a large workload.
DEMO_DIR = Path(__file__).parent
BASE_LEAN_FILES = list(DEMO_DIR.glob("test*.lean"))
# Repeat the list to simulate a much larger number of proofs.
REPETITIONS = 100
LEAN_FILES = BASE_LEAN_FILES * REPETITIONS


async def main():
    """
    Demonstrates calling verify_all with a synchronous iterator (a list of file paths).
    """
    print("--- Starting verification with a synchronous iterator ---")
    if not LEAN_FILES:
        print("No .lean files found in the demo directory. Please add some.")
        return

    print(f"Found {len(LEAN_FILES)} .lean files to verify: {[f.name for f in LEAN_FILES]}")

    # The client can be used as an async context manager.
    async with AsyncLeanClient(base_url=LEAN_SERVER_URL) as client:
        # 'LEAN_FILES' is a standard Python list, which is a synchronous iterable.
        # The function will process all items concurrently.
        results_iterator = client.verify_all(
            proofs=LEAN_FILES,
            max_workers=4,  # Limit concurrent requests
        )

        print("\n--- Verification Results ---")
        # Asynchronously iterate over the results as they are completed.
        # This allows for real-time processing of results without waiting for all jobs to finish.
        async for result in results_iterator:
            if result.error:
                print(f"Proof: {result.file_path or 'Unknown'}\n  Status: Failed\n  Error: {result.error}\n")
            else:
                print(f"Proof: {result.file_path}\n  Status: Success\n  Proved: {result.proved}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nVerification cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure the lean server is running and accessible at the configured URL.")
