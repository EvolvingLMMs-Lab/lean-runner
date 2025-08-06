# Install from Source

```sh
git clone git@github.com:EvolvingLMMs-Lab/lean-runner.git
cd lean-runner
```

```sh
uv venv
source .venv/bin/activate
uv pip install -e packages/server
```

```sh
cd playground
lake build
cd ..
```

# Run

```sh
HOST=0.0.0.0
PORT=8000
CONCURRENCY=32

source .venv/bin/activate
lean-server --host=$HOST --port=$PORT --concurrency=$CONCURRENCY --reload
```
