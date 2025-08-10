# Build Lean Server from Source

This guide walks you through setting up the Lean Server from source code, providing a high-performance REST API for executing and verifying Lean 4 mathematical proofs.

## Prerequisites

Before starting, ensure you have the following installed on your system:

- **:simple-uv: uv or :simple-anaconda: Conda**: We strongly recommend using :simple-uv: [uv](https://docs.astral.sh/uv/). You can follow [this link](https://docs.astral.sh/uv/getting-started/installation/) for installation.
- **elan**: You can follow [this tutorial](https://lean-lang.org/install/manual/) to install elan.

## Installation Steps

### 1. Clone the Repository

Choose your preferred method to clone the repository:

```bash
# Clone using HTTPS
git clone https://github.com/EvolvingLMMs-Lab/lean-runner.git
cd lean-runner
```

### 2. Set Up Python Environment

Create and activate a Python virtual environment with the required Python version:

=== ":simple-uv: uv (Linux/macOS)"
    ```bash
    # Create virtual environment with Python 3.12
    uv venv --python=3.12

    # Activate the virtual environment
    source .venv/bin/activate
    ```

=== ":simple-uv: uv (Windows)"
    ```powershell
    # Create virtual environment with Python 3.12
    uv venv --python=3.12

    # Activate the virtual environment
    .venv\Scripts\activate
    ```

=== ":simple-anaconda: Conda"
    ```bash
    # Create a new conda environment with Python 3.12
    conda create -n lean-server python=3.12
    conda activate lean-server
    ```


### 3. Install Server Package

Install the server package in editable mode to enable development:

=== ":simple-uv: uv"
    ```bash
    # Install the server package with all dependencies
    uv pip install -e packages/server
    ```

=== ":simple-anaconda: Conda"
    ```bash
    # Install the server package with all dependencies
    python -m pip install -e packages/server
    ```

### 4. Build Lean Dependencies

Build the Lean workspace and install required mathematical libraries:

```bash
# Navigate to the Lean playground
cd playground

# Build all Lean dependencies (this may take several minutes)
lake build

# Return to the project root
cd ..
```

!!! warning "Build Time"
    The initial build process downloads and compiles Mathlib4 and other dependencies, which can take 10-30 minutes depending on your system.

!!! tip "Customize Lean Dependencies"
    You can customize the Lean dependencies by modifying the `lean-runner/playground/lakefile.toml` file, or completely replace the `lean-runner/playground` directory with your own Lean workspace.

## Running the Server

### Basic Server Startup

Start the server with default settings:

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start the server
lean-server --port=8888 --concurrency=32
```

### Command Line Options

The `lean-server` command supports the following options:

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `127.0.0.1` | Host address to bind to |
| `--port` | `8000` | Port number to listen on |
| `--concurrency` | `10` | Maximum number of concurrent proof verifications |
| `--config` | `config.yaml` | Path to [configuration file](./config.md) |
| `--log-level` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

!!! example "Example Configurations"

    === "Local Development"
        ```bash
        lean-server --host=127.0.0.1 --port=8000 --reload --log-level=DEBUG
        ```

        **Features:**

        - Local access only
        - Auto-reload on code changes
        - Detailed debug logging
        - Good for development and testing

    === "Production Deployment"
        ```bash
        lean-server --host=0.0.0.0 --port=8000 --concurrency=32--log-level=INFO
        ```

        **Features:**

        - External access enabled
        - Moderate concurrency
        - Standard logging
        - Balanced performance

    === "High-Performance Setup"
        ```bash
        lean-server --host=0.0.0.0 --port=8000 --concurrency=128 --log-level=WARNING
        ```

        **Features:**

        - Maximum concurrency
        - Minimal logging overhead
        - Optimized for throughput
        - Requires sufficient system resources


## Verify Installation

Test that the server is working correctly:

### 1. Check Server Status

=== "Using curl"
    ```bash
    # In one terminal, start the server
    lean-server --host=0.0.0.0 --port=8000

    # In another terminal, test the health endpoint
    curl http://localhost:8000/health
    ```

=== "Using Browser"
    ```text
    # Open your web browser and navigate to:
    http://localhost:8000/health

    # You should see a JSON response in the browser
    ```

=== "Using Python requests"
    ```python
    import requests

    response = requests.get("http://localhost:8000/health")
    print(response.json())
    ```

**Expected response:**
```json
{"status": "ok", "message": "Lean Server is running", "version": "0.0.1"}
```

### 2. Test Proof Verification

=== "Using curl"
    ```bash
    curl -X POST http://localhost:2333/prove/check \
      -F "proof=import Mathlib.Tactic.NormNum
          theorem test : 2 + 2 = 4 := by norm_num"
    ```
    <div class="result" markdown>
    ```json
    {"success":true,"status":"finished","result":{"env":0,"messages":[]},"error_message":null}
    ```
    </div>


=== "Using Python client"
    ```python
    from lean_runner import LeanClient

    proof = """\
    import Mathlib.Tactic.NormNum

    theorem test : 1 + 1 = 2 := by norm_num
    """

    with LeanClient(base_url="http://localhost:8000") as client:
        result = client.verify(proof=proof)
        print(result.model_dump_json(indent=4))
    ```
    <div class="result" markdown>
    ```json
    {
        "success": true,
        "status": "finished",
        "result": {
            "env": 0,
            "messages": []
        },
        "error_message": null
    }
    ```
    </div>

## Next Steps

After successful installation:

1. **Read the [Client Documentation](../client/index.md)** to learn how to interact with the server
2. **Explore the [API Documentation](../api.md)** for detailed endpoint reference
