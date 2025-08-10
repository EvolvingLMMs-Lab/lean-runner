# Build Lean Server from Source

This guide walks you through setting up the Lean Server from source code, providing a high-performance REST API for executing and verifying Lean 4 mathematical proofs.

## Prerequisites

Before starting, ensure you have the following installed on your system:

- **Conda or uv**: 我们强烈建议你使用 uv，可以 follow [这个 link](https://docs.astral.sh/uv/getting-started/installation/) 进行安装。
- **elan**: 你可以 follow [这个教程](https://lean-lang.org/install/manual/) 来安装 elan。

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

=== "uv (Linux/macOS)"
    ```bash
    # Create virtual environment with Python 3.12
    uv venv --python=3.12

    # Activate the virtual environment
    source .venv/bin/activate
    ```

=== "uv (Windows)"
    ```powershell
    # Create virtual environment with Python 3.12
    uv venv --python=3.12

    # Activate the virtual environment
    .venv\Scripts\activate
    ```

=== "Conda"
    ```bash
    # Create a new conda environment with Python 3.12
    conda create -n lean-server python=3.12
    conda activate lean-server
    ```


### 3. Install Server Package

Install the server package in editable mode to enable development:

=== "uv"
    ```bash
    # Install the server package with all dependencies
    uv pip install -e packages/server
    ```

=== "Conda"
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

!!! tip "Build Time"
    The initial build process downloads and compiles Mathlib4 and other dependencies, which can take 10-30 minutes depending on your system.

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


## 🧪 Verify Installation

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
    {
        "status": "success",
        "messages": ["Proof verification completed successfully"],
        "proof_id": "abc123..."
    }
    ```
    </div>


=== "Using Python client"
    ```python
    from lean_runner import LeanClient

    proof = """\
    import Mathlib.Data.Real.Basic

    theorem test : 1 + 1 = 2 := by norm_num
    """

    with LeanClient(base_url="http://localhost:8000") as client:
        result = client.verify(proof=proof)
        print(result)
    ```
    <div class="result" markdown>
    ```json
    {
        "status": "success",
        "messages": ["Proof verification completed successfully"],
        "proof_id": "abc123..."
    }
    ```
    </div>


## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Lean Executable Not Found
**Error**: `lean: command not found` or `lake: command not found`

**Solution**:
```bash
# Ensure elan is in your PATH
source ~/.elan/env

# Or add to your shell profile
echo 'source ~/.elan/env' >> ~/.bashrc
```

#### 2. Python Version Incompatibility
**Error**: `Python 3.12+ required`

**Solution**:

=== "Linux/macOS"
    ```bash
    # Check Python version
    python --version

    # Install Python 3.12+ or use UV to manage versions
    uv python install 3.12
    uv venv --python=3.12
    ```

=== "Windows"
    ```powershell
    # Check Python version
    python --version

    # Download and install Python 3.12+ from python.org
    # Or use UV to manage versions
    uv python install 3.12
    uv venv --python=3.12
    ```

#### 3. Build Failures in Playground
**Error**: Lake build fails with dependency errors

**Solution**:
```bash
cd playground
lake clean
lake update
lake build
```

#### 4. Port Already in Use
**Error**: `Address already in use: port 8000`

**Solution**:
```bash
# Find process using the port
lsof -i :8000

# Kill the process or use a different port
lean-server --port=8001
```

#### 5. Permission Denied for Database
**Error**: Cannot write to database file

**Solution**:
```bash
# Ensure write permissions for the database directory
chmod 755 .
touch lean_server.db
chmod 644 lean_server.db
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug log level
export LOG_LEVEL=DEBUG
lean-server --log-level=DEBUG
```

### Performance Tuning

For optimal performance:

1. **Increase concurrency** based on your CPU cores:
   ```bash
   lean-server --concurrency=$(nproc)
   ```

2. **Use SSD storage** for the database and Lean cache

3. **Allocate sufficient memory** (minimum 4GB, recommended 8GB+)

4. **Monitor resource usage**:
   ```bash
   # Monitor CPU and memory usage
   htop

   # Monitor server logs
   tail -f /var/log/lean-server.log
   ```

## 🔄 Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update Python dependencies
uv pip install -e packages/server

# Rebuild Lean dependencies if needed
cd playground
lake update
lake build
cd ..

# Restart the server
lean-server
```

## 📚 Next Steps

After successful installation:

1. **Read the [Client Documentation](../client/README.md)** to learn how to interact with the server
2. **Explore the [API Documentation](../api/README.md)** for detailed endpoint reference
3. **Check out the [Examples](../../demo/)** for sample usage patterns
4. **Review the [Development Guide](../dev/README.md)** if you plan to contribute

## 🤝 Need Help?

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/EvolvingLMMs-Lab/lean-runner/issues)
2. Review the [FAQ](../faq.md)
3. Join our [Discord community](https://discord.gg/lean-runner)
4. Create a new issue with detailed error information
