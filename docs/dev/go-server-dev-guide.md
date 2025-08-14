```bash
docker create \
  --name lean-server-dev \
  -p 127.0.0.1:50051:50051 \
  --shm-size="10g" \
  --cap-add=SYS_ADMIN \
  -v $(pwd):/workspace \
  pufanyi/lean-server:0.2.0.dev0 \
  sleep infinity
```

```bash
docker start lean-server-dev
```

```bash
docker exec -it lean-server-dev bash
```

```bash
cd /workspace/server
```

```bash
go run ./cmd/server --log-level=debug
```
