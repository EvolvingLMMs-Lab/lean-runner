#!/bin/bash

# This script automates the generation of gRPC code for both the Python client
# and the Go server from the .proto files.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PROTO_DIR="proto"
PYTHON_CLIENT_DIR="client/lean_runner/grpc"
GO_SERVER_DIR="server/gen/go"

# --- Python Client Generation ---
echo "Generating Python gRPC code..."

# Create the output directory if it doesn't exist
mkdir -p "$PYTHON_CLIENT_DIR"

# Generate the gRPC code
python -m grpc_tools.protoc \
    --proto_path="$PROTO_DIR" \
    --python_out="$PYTHON_CLIENT_DIR" \
    --grpc_python_out="$PYTHON_CLIENT_DIR" \
    "$PROTO_DIR"/*.proto

# Fix the import statements in the generated gRPC files to be relative
# This is necessary for the Python package structure.
sed -i 's/^import \(.*_pb2\)/from . import \1/' "$PYTHON_CLIENT_DIR"/*_grpc.py

echo "Python gRPC code generated successfully."


# --- Go Server Generation ---
echo "Generating Go gRPC code..."

# Create the output directory if it doesn't exist
mkdir -p "$GO_SERVER_DIR"

# Generate the gRPC code
protoc \
    --proto_path="$PROTO_DIR" \
    --go_out="$GO_SERVER_DIR" \
    --go-grpc_out="$GO_SERVER_DIR" \
    "$PROTO_DIR"/*.proto

echo "Go gRPC code generated successfully."

echo "Done."
