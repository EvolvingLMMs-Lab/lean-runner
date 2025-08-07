# Lean Server Package

This package contains the core `lean-server` application, a FastAPI-based server that provides a REST API for interacting with the Lean prover.

## 📖 Overview

The server is designed to be run inside the Docker environment provided at the root of this monorepo. It exposes endpoints to perform proof checking and other Lean-related tasks.

The main API endpoint is:

- `POST /prove/check`: Accepts a `proof` and an optional `config` to run a proof.

## ⚙️ Configuration

The server's behavior can be configured via `config.yaml`. Key settings include:

- Server host and port.
- Lean process configuration.
- Proof checking timeouts.

## 🚀 Running the Server

This package is intended to be run within the development container.

1.  **Navigate to the Dev Container**:
    Follow the instructions in the [root README](../../README.md) to set up the development environment.

2.  **Install Dependencies**:
    In the container's terminal, install the package in editable mode:

    ```bash
    uv pip install -e .
    ```

    (Note: The root setup installs this automatically).

3.  **Start the Server**:
    The `pyproject.toml` file defines a script entry point. You can start the server with the following command:
    ```bash
    lean-server
    ```
    By default, it should be available at `http://localhost:8000`.
