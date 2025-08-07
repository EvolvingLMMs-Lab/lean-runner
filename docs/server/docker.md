# Installation via Docker

For a hassle-free setup of the Lean Server, we strongly recommend using Docker. This approach avoids complex local configuration of Lean and its dependencies.

The Docker image comes with `mathlib` version [v4.22.0-rc4](https://github.com/leanprover-community/mathlib4/releases/tag/v4.22.0-rc4). Custom `mathlib` versions are not supported with this method. If you require a specific version, please refer to the [build from source guide](./source.md).

## Prerequisites

Before you begin, ensure you have [Docker installed](https://docs.docker.com/engine/install/) on your system.

## 1. Pull the Docker Image

First, pull the latest server image from Docker Hub. This ensures you have the most recent version.

```bash
docker pull pufanyi/lean-server:latest
```

## 2. Running the Server

You can run the server in two modes: either as an interactive process in your terminal or as a detached process running in the background.

### Configuration Parameters

You can configure the server using the following environment variables:

- `PORT`: The port on your host machine that will forward to the server's port `8000` inside the container.
- `CONCURRENCY`: The number of concurrent requests the server can handle. The optimal value depends on your machine's resources.

### Option A: Interactive Mode (Simple Run)

This mode is useful for temporary use or for watching the server logs in real-time. The server will stop when you close your terminal session (by pressing `Ctrl+C`).

```bash
# Configuration
PORT=8888
CONCURRENCY=32

# Run the container
docker run --rm -it \
    -p $PORT:8000 \
    pufanyi/lean-server:latest \
    /app/lmms-lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
```

### Option B: Detached Mode (Run in Background)

This is the recommended mode for long-running services. The container will continue to run in the background until explicitly stopped.

```bash
# Configuration
PORT=8888
CONCURRENCY=32

# Run the container
docker run -d \
    --name lean-server \
    -p $PORT:8000 \
    pufanyi/lean-server:latest \
    /app/lmms-lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
```

### Understanding the Docker Command

| Flag         | Description                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| `docker run` | The command to create and start a new container from an image.                                               |
| `--rm`       | (Interactive Mode) Automatically removes the container when it exits.                                        |
| `-it`        | (Interactive Mode) Creates an interactive terminal session.                                                  |
| `-d`         | (Detached Mode) Runs the container in the background.                                                        |
| `--name`     | (Detached Mode) Assigns a memorable name to the container (e.g., `lean-server`).                             |
| `-p X:Y`     | Maps port `X` on the host to port `Y` inside the container. Our server runs on port `8000` in the container. |

## 3. Verifying the Server

After starting the container, you can verify that the server is running by sending a health check request. Open a new terminal and run:

```bash
curl http://localhost:8888/health
```

If the server is running correctly, you should receive a response like:

```json
{ "status": "ok" }
```

## 4. Managing the Container

If you are running the server in detached mode, you can use the following commands to manage it.

### Viewing Logs

To see the real-time output from the server:

```bash
docker logs -f lean-server
```

### Stopping the Server

To gracefully stop the running container:

```bash
docker stop lean-server
```

### Restarting the Server

If you have stopped the container, you can restart it without having to run the full `docker run` command again:

```bash
docker start lean-server
```
