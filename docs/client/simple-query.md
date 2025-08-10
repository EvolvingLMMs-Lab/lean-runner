# Simple Query

This guide will walk you through performing a simple proof verification using both synchronous and asynchronous clients.

## Synchronous Client

The synchronous client is straightforward to use and is suitable for most common use cases.

### API Reference: `verify`

The `client.verify()` method sends a proof to the server and synchronously waits for the verification result.

!!! abstract "Function Signature"
    ```python
    def verify(
        self,
        proof: str | Path | os.PathLike,
        config: ProofConfig | None = None
    ) -> ProofResult:
    ```

#### Parameters

-   **`proof`** (`str | Path | os.PathLike`): The proof to be verified. This can be provided in several ways:
    -   A string containing the Lean code.
    -   A `pathlib.Path` object pointing to a `.lean` file.
    -   A string representing the path to a `.lean` file.

-   **`config`** (`ProofConfig | None`, optional): A configuration object to customize the verification process. If not provided, default settings are used. See the [Proof Configuration](./config.md) page for details on available options.

#### Returns

-   **`ProofResult`**: A Pydantic model containing the verification results, including status, and any potential errors.

### Example

!!! example "Verifying a proof"
    Here's how to verify a simple proof using the `LeanClient`:

    ```python
    from lean_runner import LeanClient

    # Initialize the client with the server's base URL
    client = LeanClient("http://localhost:8000")

    # Define the proof as a string
    proof_content = """
    import Mathlib.Tactic.NormNum
    theorem test : 2 + 2 = 4 := by norm_num
    """

    # Verify the proof
    result = client.verify(proof_content)

    # Print the result
    print(result.model_dump_json(indent=2))

    # The client should be closed when no longer needed
    client.close()
    ```

!!! example "Using a `with` statement"
    You can use a `with` statement to manage the client's lifecycle automatically:

    ```python
    from lean_runner import LeanClient

    with LeanClient("http://localhost:8000") as client:
        proof_content = """
        import Mathlib.Tactic.NormNum
        theorem test : 2 + 2 = 4 := by norm_num
        """
        result = client.verify(proof_content)
        print(result.model_dump_json(indent=2))
    ```

## Asynchronous Client

The asynchronous client is ideal for applications that require high concurrency and non-blocking I/O.

### API Reference: `verify`

The `client.verify()` method sends a proof to the server and asynchronously awaits the verification result.

!!! abstract "Function Signature"
    ```python
    async def verify(
        self,
        proof: str | Path | os.PathLike | AnyioPath,
        config: ProofConfig | None = None,
    ) -> ProofResult:
    ```

#### Parameters

-   **`proof`** (`str | Path | os.PathLike | AnyioPath`): The proof to be verified. This can be provided as:
    -   A string containing the Lean code.
    -   A `pathlib.Path` or `anyio.Path` object pointing to a `.lean` file.
    -   A string representing the path to a `.lean` file.

-   **`config`** (`ProofConfig | None`, optional): A configuration object to customize the verification process. If not provided, default settings are used. See the [Proof Configuration](./config.md) page for details on available options.

#### Returns

-   **`ProofResult`**: A Pydantic model containing the verification results.

### Example

!!! example "Verifying a proof asynchronously"
    Here's the same example using the `AsyncLeanClient`:

    ```python
    import asyncio
    from lean_runner import AsyncLeanClient

    async def main():
        # Initialize the async client
        async with AsyncLeanClient("http://localhost:8000") as client:
            proof_content = """
            import Mathlib.Tactic.NormNum
            theorem test : 2 + 2 = 4 := by norm_num
            """
            result = await client.verify(proof_content)
            print(result.model_dump_json(indent=2))

    if __name__ == "__main__":
        asyncio.run(main())
    ```
    In this example, `async with` ensures the client session is properly closed. The `await client.verify()` call performs the verification without blocking the event loop.
