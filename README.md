# LMMs Lean Runner

A high-performance server and client system for running and verifying Lean 4 theorem proofs. This project provides a FastAPI-based server that can execute Lean proofs asynchronously and a Python client library for interacting with the server.

## Overview

LMMs Lean Runner consists of two main components:

- **Lean Server**: A FastAPI-based server that manages and executes Lean theorem proofs with configurable concurrency
- **Lean Client**: A Python client library with both synchronous and asynchronous interfaces for submitting and monitoring proof verification

## Features

- **Asynchronous Proof Processing**: Submit proofs for background processing and poll for results
- **Concurrent Execution**: Configure the number of concurrent Lean processes for optimal performance
- **Flexible Client**: Support for both synchronous and asynchronous Python clients
- **Rich Status Monitoring**: Track proof verification status with detailed progress information
- **Database Persistence**: SQLite-based storage for proof history and results
- **Configurable Timeout**: Set custom timeouts for long-running proofs

## Installation

### Prerequisites

- Python 3.12 or higher
- Lean 4 installed on your system
- Git

### Clone the Repository

```bash
git clone https://github.com/EvolvingLMMs-Lab/lmms-lean-runner.git
cd lmms-lean-runner
```

### Server Installation

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install the server package
uv pip install -e packages/server

# Build the Lean playground
cd playground
lake build
cd ..
```

### Client Installation

```bash
# Install the client package
uv pip install -e packages/client
```

### Development Installation

For development with all dependencies:

```bash
# Install with dev dependencies
uv pip install -e . --dev
```

## Quick Start

### Starting the Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the server with default settings
lean-server --host=0.0.0.0 --port=8080 --concurrency=4
```

Server options:

- `--host`: Host address to bind to (default: 0.0.0.0)
- `--port`: Port to listen on (default: 8080)
- `--concurrency`: Number of concurrent Lean processes (default: 4)
- `--reload`: Enable auto-reload for development

### Using the Client

#### Simple Verification (Synchronous)

```python
from pathlib import Path
from lean_client import LeanClient

# Initialize the client
with LeanClient(base_url="http://localhost:8080") as client:
    # Path to your .lean file
    proof_file = Path("test.lean")

    # Send for verification and wait for result
    result = client.verify(proof=proof_file)

    print(f"Status: {result.status}")
    print(f"Result: {result.result}")
```

#### Asynchronous Operations

```python
import asyncio
from pathlib import Path
from lean_client import AsyncLeanClient

async def verify_proof():
    async with AsyncLeanClient(base_url="http://localhost:8080") as client:
        proof_file = Path("test.lean")
        result = await client.verify(proof=proof_file)
        print(f"Status: {result.status}")
        return result

# Run the async function
asyncio.run(verify_proof())
```

#### Submit and Poll Pattern (for long-running proofs)

```python
from lean_client import LeanClient
import time

with LeanClient(base_url="http://localhost:8080") as client:
    # Submit proof for background processing
    proof = client.submit(proof="theorem example : 2 + 2 = 4 := rfl")
    print(f"Proof ID: {proof.id}")

    # Poll for result
    while True:
        result = client.get_result(proof=proof)
        print(f"Status: {result.status}")

        if result.status in ["FINISHED", "ERROR"]:
            print(f"Final result: {result.result}")
            break

        time.sleep(1)
```

## Project Structure

```
lmms-lean-runner/
├── packages/
│   ├── client/          # Python client library
│   │   └── lean_client/
│   │       ├── client/  # Client implementations
│   │       └── proof/   # Proof data models
│   └── server/          # FastAPI server
│       └── lean_server/
│           ├── app/     # FastAPI application
│           ├── manager/ # Proof execution management
│           ├── database/# SQLite persistence
│           └── config/  # Server configuration
├── playground/          # Lean 4 workspace for proof execution
├── demo/               # Example scripts and Lean files
└── docs/               # Documentation
    ├── client/         # Client documentation
    └── server/         # Server documentation
```

## API Endpoints

### POST `/prove/submit`

Submit a proof for verification. Returns immediately with a proof ID.

**Request:**

- `proof`: Lean proof content (string)
- `config`: Optional configuration (JSON)

**Response:**

- `id`: Unique proof identifier
- `status`: Initial status ("PENDING")

### POST `/prove/check`

Submit a proof and wait for the result (synchronous verification).

**Request:**

- `proof`: Lean proof content (string)
- `config`: Optional configuration (JSON)

**Response:**

- `id`: Unique proof identifier
- `status`: Final status ("FINISHED" or "ERROR")
- `result`: Verification result or error message

### GET `/prove/{proof_id}`

Get the status and result of a submitted proof.

**Response:**

- `id`: Proof identifier
- `status`: Current status ("PENDING", "RUNNING", "FINISHED", "ERROR")
- `result`: Result if available
- `messages`: Warning or error messages

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lean_server --cov=lean_client
```

### Code Quality

```bash
# Format code
black packages/

# Lint
ruff check packages/

# Type checking
mypy packages/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Configuration

The server can be configured through environment variables or a YAML configuration file:

- `LEAN_SERVER_CONFIG`: Path to configuration file
- `LEAN_SERVER_HOST`: Server host address
- `LEAN_SERVER_PORT`: Server port
- `LEAN_SERVER_CONCURRENCY`: Number of concurrent Lean processes

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/EvolvingLMMs-Lab/lmms-lean-runner/issues).

## Authors

- [Pu Fanyi]
- [Oscar Qian]
- [Bo Li]

## Acknowledgments

Built with:

- [Lean 4](https://github.com/leanprover/lean4) - Theorem prover
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [httpx](https://www.python-httpx.org/) - HTTP client
