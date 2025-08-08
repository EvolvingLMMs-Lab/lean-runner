<picture>
	<source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo/logo-wt-dark.webp">
	<img align="left" alt="i" src="docs/assets/logo/logo-wt.webp">
</picture>

A high-performance server and client system for executing and verifying Lean 4 mathematical proofs. This project provides a FastAPI-based REST API server that interfaces with the Lean theorem prover, along with Python client libraries for both synchronous and asynchronous operations.

## Features

- **REST API Server**: FastAPI-based server for processing Lean proofs
- **Dual Client Support**: Both synchronous and asynchronous Python clients
- **Concurrent Processing**: Semaphore-based concurrency control for handling multiple proof requests
- **Database Persistence**: SQLite storage for proof results with unique identifiers
- **Flexible Input**: Accept proofs as strings, file paths, or Path objects
- **Comprehensive Error Handling**: Detailed error reporting and status tracking
- **Mathlib Integration**: Full support for Mathlib4 mathematical library

## Architecture

```
lean-runner/
├── packages/
│   ├── server/          # FastAPI server implementation
│   │   └── lean_server/
│   │       ├── app/     # API endpoints and server setup
│   │       ├── proof/   # Lean proof execution logic
│   │       ├── manager/ # Proof job management
│   │       └── database/# SQLite persistence layer
│   └── client/          # Python client libraries
│       └── lean_client/
│           ├── client/  # Sync and async client implementations
│           └── proof/   # Shared data models
├── playground/          # Lean workspace with dependencies
└── demo/               # Example scripts and test files
```

## Installation

### Prerequisites

- Python 3.12 or higher
- Lean 4 (installed via elan)
- UV package manager (recommended) or pip

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/EvolvingLMMs-Lab/lean-runner.git
cd lean-runner
```

2. **Set up Python environment:**
```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
uv pip install -e packages/server
uv pip install -e packages/client
```

3. **Build Lean dependencies:**
```bash
cd playground
lake build
cd ..
```

4. **Configure the server:**

Edit `packages/server/config.yaml` to set your paths:
```yaml
lean:
  executable: /path/to/your/.elan/bin/lake
  workspace: /path/to/lean-runner/playground
sqlite:
  database_path: /path/to/lean-runner/lean_server.db
```

5. **Start the server:**
```bash
lean-server --host 0.0.0.0 --port 8000
```

## Usage

### Server API Endpoints

- `POST /prove/check` - Synchronously verify a proof
- `POST /prove/submit` - Submit a proof for asynchronous processing
- `GET /prove/result/{proof_id}` - Retrieve proof results by ID

### Python Client Examples

#### Synchronous Client
```python
from lean_client import LeanClient
from pathlib import Path

# Connect to server
with LeanClient(base_url="http://localhost:8000") as client:
    # Verify a proof string
    result = client.verify(
        proof="theorem test : 1 + 1 = 2 := by norm_num"
    )
    print(result)

    # Verify a proof from file
    result = client.verify(proof=Path("path/to/proof.lean"))
    print(result)
```

#### Asynchronous Client
```python
import asyncio
from lean_client import AsyncLeanClient

async def verify_proof():
    async with AsyncLeanClient(base_url="http://localhost:8000") as client:
        # Submit proof for processing
        proof_id = await client.submit(
            proof="theorem test : 2 + 2 = 4 := by norm_num"
        )

        # Get result
        result = await client.get_result(proof_id)
        print(result)

asyncio.run(verify_proof())
```

#### Batch Processing
```python
import asyncio
from lean_client import AsyncLeanClient

async def verify_multiple():
    async with AsyncLeanClient(base_url="http://localhost:8000") as client:
        proofs = [
            "theorem test1 : 1 + 1 = 2 := by norm_num",
            "theorem test2 : 2 * 3 = 6 := by norm_num",
            "theorem test3 : 5 - 3 = 2 := by norm_num"
        ]

        # Submit all proofs concurrently
        tasks = [client.verify(proof=p) for p in proofs]
        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            print(f"Proof {i+1}: {result.status}")

asyncio.run(verify_multiple())
```

## Configuration

### Server Configuration (`config.yaml`)

```yaml
lean:
  executable: /path/to/lake  # Lean build tool executable
  workspace: /path/to/playground  # Lean workspace directory

sqlite:
  database_path: /path/to/database.db  # SQLite database file
  timeout: 10  # Database operation timeout

logging:
  version: 1
  handlers:
    default:
      class: "rich.logging.RichHandler"
      level: "INFO"
```

### Proof Configuration Options

When submitting proofs, you can specify:
- `tactics`: Enable tactics in proof
- `ast`: Output abstract syntax tree
- `premises`: Extract premises from proof
- `hide_warnings`: Filter out Lean warning messages

## API Reference

### LeanClient (Synchronous)

```python
class LeanClient:
    def verify(self, proof: str | Path, **config) -> ProofResult
    def submit(self, proof: str | Path, **config) -> str
    def get_result(self, proof_id: str) -> ProofResult
```

### AsyncLeanClient (Asynchronous)

```python
class AsyncLeanClient:
    async def verify(self, proof: str | Path, **config) -> ProofResult
    async def submit(self, proof: str | Path, **config) -> str
    async def get_result(self, proof_id: str) -> ProofResult
```

### ProofResult Model

```python
class ProofResult:
    status: str  # "success", "failure", or "error"
    messages: list[str]  # Output messages from Lean
    proof_id: Optional[str]  # Unique identifier for the proof
```

## Examples

Check the `demo/` directory for complete examples:
- `simple_query.py` - Basic client usage with concurrent requests
- `submit_query_sync.py` - Synchronous proof submission workflow
- `submit_query_async.py` - Asynchronous proof submission workflow
- `test1.lean` to `test4.lean` - Sample Lean proof files

## Development

### Project Structure

- **Server Package** (`packages/server/`): FastAPI application with proof processing engine
- **Client Package** (`packages/client/`): Python client libraries for API interaction
- **Playground** (`playground/`): Lean workspace with Mathlib and other dependencies
- **Documentation** (`docs/`): API and usage documentation

### Running Tests

```bash
# Run server tests
cd packages/server
pytest

# Run client tests
cd packages/client
pytest
```

### Building from Source

```bash
# Install in development mode
uv pip install -e packages/server[dev]
uv pip install -e packages/client[dev]

# Build Lean dependencies
cd playground
lake update
lake build
```

## Lean Dependencies

The project includes the following Lean 4 libraries:
- **Mathlib4**: Comprehensive mathematical library
- **REPL**: Interactive evaluation support
- **Aesop**: Automated reasoning tactics

## Troubleshooting

### Common Issues

1. **Lean executable not found**: Ensure Lean 4 is installed via elan and update the path in `config.yaml`

2. **Database permission errors**: Check write permissions for the database path specified in configuration

3. **Import errors**: Make sure to install packages in the correct order (server first, then client)

4. **Timeout errors**: Increase timeout values in client initialization for complex proofs

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export LOG_LEVEL=DEBUG
lean-server
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

```bibtex
@misc{fanyi2025leanrunner,
  title={Lean-Runner: A High-Performance Server and Client System for Lean 4 Mathematical Proofs},
  author={Fanyi Pu, Oscar Qian, Yezhen Wang, Bo Li},
  year={2025},
  publisher={GitHub},
  howpublished={\url{https://github.com/EvolvingLMMs-Lab/lean-runner}},
}
```

## Acknowledgments

- Lean 4 development team
- Mathlib contributors
- FastAPI framework developers
