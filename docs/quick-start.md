# Quick Start

## Server

!!! tip "Docker Engine Required"
    Run the Lean-Runner server using Docker. If Docker is not installed, follow this [tutorial](https://docs.docker.com/engine/install/) to install it.

For existing users, pull the latest image to ensure you have the most recent version.

```sh
docker pull pufanyi/lean-server:latest
```

Start the server with a single `docker run` command:

```sh
PORT=8080
CONCURRENCY=32
DB_PATH=./database

docker run --rm -it \
    -p $PORT:8000 \
    -v $DB_PATH:/app/database \
    pufanyi/lean-server:latest \
    /app/lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
```

## Client

Install the Lean-Runner client from PyPI:

=== "pip"

    ```bash
    pip install lean-runner
    ```

=== "uv"

    ```bash
    uv pip install lean-runner
    ```

Use `LeanClient` to verify a proof. The client supports both synchronous and asynchronous operations:

!!! example "Lean proof verification"

    === "Synchronous"

        ```python
        from lean_runner import LeanClient

        # Define a simple Lean 4 proof
        proof = """\
        import Mathlib.Tactic.NormNum
        theorem test : 2 + 2 = 4 := by norm_num
        """

        # Create client and verify the proof
        with LeanClient(base_url="http://localhost:8080") as client:
            result = client.verify(proof=proof)
            print(result)
        ```

    === "Asynchronous"

        ```python
        import asyncio
        from lean_runner import AsyncLeanClient

        # Define a simple Lean 4 proof
        proof = """\
        import Mathlib.Tactic.NormNum
        theorem test : 2 + 2 = 4 := by norm_num
        """

        async def main():
            # Create async client and verify the proof
            async with AsyncLeanClient(base_url="http://localhost:8080") as client:
                result = await client.verify(proof=proof)
                print(result)

        asyncio.run(main())
        ```
