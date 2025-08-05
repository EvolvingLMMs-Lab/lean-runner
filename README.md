# Lean Server

# WARNING: This is currently AI-generated and not yet functional.

A FastAPI-based server to interact with the Lean Theorem Prover, with a Python client library.

## Project Structure

This is a multipackage project using uv workspace:

```
lean-server/
├── pyproject.toml          # Workspace configuration
├── packages/
│   ├── client/            # Lean client library
│   │   └── pyproject.toml
│   └── server/            # Lean server application
│       └── pyproject.toml
```

## Development Setup

### Prerequisites

- Python 3.12+
- uv (install with `pip install uv`)

### Initial Setup

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Initialize the workspace**:
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

### Working with Packages

#### Install dependencies for all packages:
```bash
uv sync
```

#### Install dependencies for a specific package:
```bash
uv sync --package lean-client
uv sync --package lean-server
```

#### Add a dependency to a specific package:
```bash
uv add --package lean-client requests
uv add --package lean-server redis
```

#### Add a development dependency:
```bash
uv add --dev --package lean-client pytest
uv add --dev --package lean-server httpx
```

#### Run tests for all packages:
```bash
uv run pytest
```

#### Run tests for a specific package:
```bash
uv run --package lean-client pytest
uv run --package lean-server pytest
```

#### Build all packages:
```bash
uv build
```

#### Build a specific package:
```bash
uv build --package lean-client
uv build --package lean-server
```

#### Install packages in development mode:
```bash
uv pip install -e packages/client
uv pip install -e packages/server
```

### Package Management

#### Adding a new package:
1. Create a new directory in `packages/`
2. Add a `pyproject.toml` file
3. Add the package to the workspace members in the root `pyproject.toml`

#### Removing a package:
1. Remove the package directory
2. Remove it from the workspace members in the root `pyproject.toml`

### Common Commands

- `uv sync` - Install all dependencies
- `uv add <package>` - Add dependency to workspace
- `uv add --dev <package>` - Add development dependency
- `uv run <command>` - Run command in workspace environment
- `uv build` - Build all packages
- `uv publish` - Publish packages to PyPI

## Package Details

### lean-client
A Python client library for interacting with the Lean Theorem Prover Server API.

**Key dependencies:**
- aiohttp>=3.9.0
- pydantic>=2.0.0

### lean-server
A FastAPI-based server application for the Lean Theorem Prover.

**Key dependencies:**
- fastapi>=0.116.1
- uvicorn>=0.35.0
- pydantic>=2.11.7
- aiohttp>=3.12.15

## Development Workflow

1. **Start development**:
   ```bash
   uv sync
   source .venv/bin/activate
   ```

2. **Make changes** to packages in `packages/`

3. **Test changes**:
   ```bash
   uv run pytest
   ```

4. **Build and install**:
   ```bash
   uv build
   uv pip install -e packages/client
   uv pip install -e packages/server
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Submit a pull request

## License

MIT License
