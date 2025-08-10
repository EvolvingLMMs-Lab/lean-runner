# Asynchronous Submission and Retrieval

This guide covers the process of submitting a proof for verification without waiting for the result, and then retrieving the result later. This is useful for long-running proofs or for integrating into job queue systems.

## Synchronous Client

The synchronous client allows you to submit a proof and then poll for the result at a later time.

### API Reference: `submit` and `get_result`

First, `client.submit()` sends a proof to the server and returns a `Proof` object, which acts as a handle for the verification job. Then, `client.get_result()` uses this handle to fetch the result.

!!! abstract "Function Signatures"
    ```python
    def submit(
        self,
        proof: str | Path | os.PathLike,
        config: ProofConfig | None = None
    ) -> Proof:

    def get_result(self, proof: Proof) -> ProofResult:
    ```

#### Parameters

-   **`submit.proof`** (`str | Path | os.PathLike`): The proof content to be verified (string, `pathlib.Path`, or path string).
-   **`submit.config`** (`ProofConfig | None`, optional): Configuration for the verification. See [Proof Configuration](./config.md) for details.
-   **`get_result.proof`** (`Proof`): The `Proof` object returned by the `submit` method.

#### Returns

-   **`submit`**: Returns a `Proof` object containing metadata about the submitted job, including its unique ID.
-   **`get_result`**: Returns a `ProofResult` object with the full verification result.

### Example

!!! example "Submitting a proof and getting the result"
    The following example shows how to submit a proof and then retrieve its result. Note that in a real-world application, you might add a delay or a retry mechanism between submission and result retrieval.

    ```python
    from lean_runner import LeanClient

    with LeanClient("http://localhost:8000") as client:
        proof_content = (
            "import Mathlib.Tactic.NormNum\n"
            "theorem test : 2 + 2 = 4 := by norm_num"
        )

        # Submit the proof
        submitted_proof = client.submit(proof_content)
        print(f"Proof submitted with ID: {submitted_proof.id}")

        # Retrieve the result later
        # In a real scenario, you might wait here
        result = client.get_result(submitted_proof)
        print(result.model_dump_json(indent=2))
    ```

## Asynchronous Client

The asynchronous client provides non-blocking methods to submit a proof and fetch its result, making it ideal for highly concurrent applications.

### API Reference: `submit` and `get_result`

The `client.submit()` coroutine sends the proof, and `client.get_result()` fetches the outcome.

!!! abstract "Function Signatures"
    ```python
    async def submit(
        self,
        proof: str | Path | os.PathLike | AnyioPath,
        config: ProofConfig | None = None,
    ) -> Proof:

    async def get_result(self, proof: Proof) -> ProofResult:
    ```

#### Parameters

-   **`submit.proof`** (`str | Path | os.PathLike | AnyioPath`): The proof content (string, `pathlib.Path`, `anyio.Path`, or path string).
-   **`submit.config`** (`ProofConfig | None`, optional): Verification configuration. See [Proof Configuration](./config.md).
-   **`get_result.proof`** (`Proof`): The `Proof` object returned by `submit`.

#### Returns

-   **`submit`**: A `Proof` object.
-   **`get_result`**: A `ProofResult` object.

### Example

!!! example "Asynchronous submit and retrieve"
    This example demonstrates the async workflow.

    ```python
    import asyncio
    from lean_runner import AsyncLeanClient

    async def main():
        async with AsyncLeanClient("http://localhost:8000") as client:
            proof_content = (
                "import Mathlib.Tactic.NormNum\n"
                "theorem test : 2 + 2 = 4 := by norm_num"
            )

            # Submit the proof without blocking
            submitted_proof = await client.submit(proof_content)
            print(f"Proof submitted with ID: {submitted_proof.id}")

            # Wait and retrieve the result
            await asyncio.sleep(1) # Simulate waiting
            result = await client.get_result(submitted_proof)
            print(result.model_dump_json(indent=2))

    if __name__ == "__main__":
        asyncio.run(main())
    ```
