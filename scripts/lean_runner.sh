#!/bin/bash

set -eu

COMMAND='cd /workspace/prover/ && source .venv/bin/activate && python -m prover.lean_runner'

docker exec prover zsh -c "${COMMAND}"
