# Docker

Simple run:

```bash
PORT=8888
CONCURRENCY=32

docker run --rm -it \
  -p $PORT:8000 \
  pufanyi/lean-server:latest \
  /app/lmms-lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
```

Run in background:

```bash
PORT=8888
CONCURRENCY=32

docker run -d \
  --name lean-server \
  -p $PORT:8000 \
  pufanyi/lean-server:latest \
  /app/lmms-lean-runner/.venv/bin/lean-server --concurrency=$CONCURRENCY
```
