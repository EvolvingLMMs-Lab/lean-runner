#!/bin/bash

set -eu

COMMAND='
  cd ~/playground && \
  echo "=========================================" && \
  echo "Pulling latest changes from git..." && \
  echo "=========================================" && \
  git pull && \
  echo "" && \
  echo "=========================================" && \
  echo "Building playground with lake..." && \
  echo "=========================================" && \
  /root/.elan/bin/lake build
'

sudo docker exec prover zsh -c "${COMMAND}"