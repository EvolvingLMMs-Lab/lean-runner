#!/bin/bash

set -eu

COMMAND='cd /workspace/lean-server/ && source .venv/bin/activate && lean-server'

docker exec -e PYTHONUNBUFFERED=1 -e FORCE_COLOR=1 -e TERM=xterm-256color lean-server zsh -c "${COMMAND}"
