# Install with Docker

If you just want to use the Lean Server, we highly recommend installing it via Docker. This will bypass the various configurations of Lean.

We currently do not support custom Math versions. The Docker image comes with the latest version [v4.22.0-rc4](https://github.com/leanprover-community/mathlib4/releases/tag/v4.22.0-rc4). If you need a custom version, please refer to the [source installation guide](./source.md).

!!! tip "Install and run"

    === "Simple run"

        ```bash
        PORT=8888
        CONCURRENCY=32

        docker run --rm -it \
            -p $PORT:8000 \
            pufanyi/lean-server:latest \
            /app/lmms-lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
        ```

    === "Run in background"

        ```bash
        PORT=8888
        CONCURRENCY=32

        docker run -d \
            --name lean-server \
            -p $PORT:8000 \
            pufanyi/lean-server:latest \
            /app/lmms-lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
        ```

        To view the logs, you can run:

        ```bash
        docker logs lean-server
        ```

        To stop the server, you can run:

        ```bash
        docker stop lean-server
        ```
