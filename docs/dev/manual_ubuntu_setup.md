# Manual Setup Guide for Ubuntu

This document provides a step-by-step guide on how to set up the `lean-runner` environment and run the server from a clean Ubuntu system, such as a fresh Docker container.

## 1. Start a Clean Ubuntu Container

First, start an interactive Ubuntu container. We will map port `8000` from the container to our host machine to access the server later.

```sh
docker run -it --name lean-server -p 8080:8080 ubuntu:latest /bin/bash
```

All subsequent commands should be run inside this container's shell.

## 2. Update System and Install Dependencies

Update the package list and install essential tools like `git`, `curl`, and `python`.

```sh
apt-get update
apt-get install -y git curl
```

## 3. Install `uv`

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 4. Install Lean and `lake`

Install `elan`, the Lean toolchain manager. This will also install `lake`, the build system.

```sh
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
```

After installation, you need to add `elan` to your current shell's `PATH`.

```sh
source /root/.elan/env
```
*Note: If you are not running as root, the path will be `~/.elan/env`.*

## 5. Clone the Project

Clone the repository from GitHub.

```sh
git clone https://github.com/EvolvingLMMs-Lab/lean-runner.git
cd lean-runner
```

## 6. Build Lean Dependencies

Navigate to the `playground` directory and use `lake` to build the Lean dependencies.

```sh
uv venv
```

## 7. Install Python Packages

Use `uv` to install the `lmms-lean-server` package and its dependencies in editable mode.

```sh
uv pip install -e packages/server
```

## 8. Run the Server

Now you can start the server. It will run inside the container on port `8000`.

```sh
lean-server --host 0.0.0.0 --port 8080
```
- `--host 0.0.0.0` is important to make the server accessible from outside the container.

Because we started the container with `-p 8000:8000`, you can now access the server from your host machine's browser at `http://localhost:8000`.
