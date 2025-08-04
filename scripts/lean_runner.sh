#!/bin/bash

set -eu

COMMAND='cd /workspace/lean-server/ && source .venv/bin/activate && python -m lean_server.proof.lean'

docker exec lean-server zsh -c "${COMMAND}"
