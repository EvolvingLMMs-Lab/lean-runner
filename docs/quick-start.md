# Quick Start

## Server

我们需要使用 Docker 来运行 Lean-Runner 的 server 端。如果你没有安装 Docker，请 follow 这个[教程](https://docs.docker.com/engine/install/) 进行安装。

如果你不是第一次运行 Lean-Runner，你需要使用 docker pull 来确保你使用的是最新的镜像。

```sh
docker pull pufanyi/lean-server:latest
```

接下来，使用一句 `docker run` 启动 server。

```sh
PORT=8080
CONCURRENCY=4

docker run --rm -it \
    -p $PORT:8000 \
    pufanyi/lean-server:latest \
    /app/lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
```

## Client

使用 PyPI 安装 Lean-Runner 的 client 端。

=== "pip"

    ```bash
    pip install lean-runner
    ```

=== "uv"

    ```bash
    uv pip install lean-runner
    ```

接下来，使用 LeanClient 来验证一个证明。

=== "Synchronous"

    ```python
    from lean_runner import LeanClient

    proof = """\
    import data.real.basic

    theorem test : 1 + 1 = 2 := by norm_num
    """

    with LeanClient(base_url="http://localhost:8000") as client:
        result = client.verify(proof=proof)
        print(result)
    ```

=== "Asynchronous"

    ```python
    import asyncio
    from lean_runner import AsyncLeanClient

    proof = """\
    import data.real.basic
    
    theorem test : 1 + 1 = 2 := by norm_num
    """

    async def main():
        async with AsyncLeanClient(base_url="http://localhost:8000") as client:
            result = await client.verify(proof=proof)
            print(result)

    asyncio.run(main())
    ```
