#!/bin/bash

set -eu

COMMAND='cd /workspace/prover/ && source .venv/bin/activate && /root/.local/bin/uv pip install vllm --torch-backend=auto && /root/.local/bin/uv pip install -e .'

docker exec prover zsh -c "${COMMAND}"
