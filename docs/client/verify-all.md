# Bulk Verification

This guide explains how to verify multiple proofs efficiently in a single batch operation using the `verify_all` method.

## Synchronous Client

The synchronous `verify_all` method is ideal for processing a collection of proofs when you want to handle them concurrently without the complexity of async programming. It uses a thread pool to manage concurrent requests.

### API Reference: `verify_all`

The `client.verify_all()` method sends a collection of proofs to the server and yields results as they are completed. This approach is memory-efficient as it doesn't wait for all proofs to be verified before returning results.

!!! abstract "Function Signature"
    ```python
    def verify_all(
        self,
        proofs: Iterable[str | Path | os.PathLike],
        config: ProofConfig | None = None,
        total: int | None = None,
        max_workers: int = 128,
        progress_bar: bool = True,
    ) -> Iterable[ProofResult]:
    ```

#### Parameters

-   **`proofs`** (`Iterable[str | Path | os.PathLike]`): An iterable of proofs to be verified. Each item can be:
    -   A string containing Lean code.
    -   A `pathlib.Path` object to a `.lean` file.
    -   A string path to a `.lean` file.
-   **`config`** (`ProofConfig | None`, optional): Configuration for the verification process. See the [Proof Configuration](./config.md) for details.
-   **`total`** (`int | None`, optional): The total number of proofs. If not provided, it's inferred if `proofs` has a `__len__` method.
-   **`max_workers`** (`int`): The maximum number of concurrent threads to use.
-   **`progress_bar`** (`bool`): If `True`, a progress bar is displayed.

#### Returns

-   **`Iterable[ProofResult]`**: An iterator that yields `ProofResult` objects as each verification completes.

### Example

!!! example "Verifying a list of proofs"
    Here's how to verify a list of proofs concurrently.

    ```python
    from lean_runner import LeanClient

    with LeanClient("http://localhost:8000") as client:
        proofs = [
            "theorem test1 : 1 + 1 = 2 := by norm_num",
            "theorem test2 : 2 * 2 = 4 := by norm_num",
            "theorem test3 : 3 - 1 = 2 := by norm_num",
        ]

        results = client.verify_all(proofs)

        for result in results:
            print(result.model_dump_json(indent=2))
    ```

## Asynchronous Client

The asynchronous `verify_all` method offers the highest performance for I/O-bound tasks, making it perfect for applications with high concurrency needs.

### API Reference: `verify_all`

The `client.verify_all()` coroutine processes an iterable (or async iterable) of proofs, using an efficient producer-consumer pattern to manage the workload.

!!! abstract "Function Signature"
    ```python
    async def verify_all(
        self,
        proofs: Iterable[str | Path | os.PathLike | AnyioPath]
        | AsyncIterable[str | Path | os.PathLike | AnyioPath],
        config: ProofConfig | None = None,
        total: int | None = None,
        max_workers: int = 128,
        progress_bar: bool = True,
    ) -> AsyncIterable[ProofResult]:
    ```

#### Parameters

-   **`proofs`** (`Iterable | AsyncIterable`): An iterable or async iterable of proofs. Each item can be:
    -   A string of Lean code.
    -   A `pathlib.Path` or `anyio.Path` to a `.lean` file.
    -   A string path to a `.lean` file.
-   **`config`** (`ProofConfig | None`, optional): Verification configuration. See [Proof Configuration](./config.md).
-   **`total`** (`int | None`, optional): The total number of proofs for the progress bar.
-   **`max_workers`** (`int`): The maximum number of concurrent async tasks.
-   **`progress_bar`** (`bool`): If `True`, a progress bar is shown.

#### Returns

-   **`AsyncIterable[ProofResult]`**: An async iterator that yields `ProofResult` objects as they complete.

### Example

!!! example "Verifying proofs asynchronously"
    The `async for` loop is used to iterate over the results from the async generator.

    ```python
    import asyncio
    from lean_runner import AsyncLeanClient

    async def main():
        async with AsyncLeanClient("http://localhost:8000") as client:
            proofs = [
                "theorem test1 : 1 + 1 = 2 := by norm_num",
                "theorem test2 : 2 * 2 = 4 := by norm_num",
                "theorem test3 : 3 - 1 = 2 := by norm_num",
            ]

            results = client.verify_all(proofs)

            async for result in results:
                print(result.model_dump_json(indent=2))

    if __name__ == "__main__":
        asyncio.run(main())
    ```
