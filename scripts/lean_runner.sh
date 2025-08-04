#!/bin/bash

set -eu

COMMAND='cd /workspace/prover/ && source .venv/bin/activate && python -m prover.proof.lean'

docker exec prover zsh -c "${COMMAND}"
