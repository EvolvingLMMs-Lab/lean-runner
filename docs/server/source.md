# 🚀 Install Lean Server from Source

This guide walks you through setting up the Lean Server from source code, providing a high-performance REST API for executing and verifying Lean 4 mathematical proofs.

## 📋 Prerequisites

Before starting, ensure you have the following installed on your system:

- **Python 3.12+**: Required for running the server
- **Git**: For cloning the repository
- **Lean 4**: Install via [elan](https://github.com/leanprover/elan) (Lean toolchain manager)
- **UV Package Manager**: Recommended for Python dependency management
- **Lake**: Lean build tool (installed with elan)

### Installing Prerequisites

#### Install Lean 4 and Lake

=== "Linux/macOS"
    ```bash
    # Install elan (Lean toolchain manager)
    curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
    source ~/.elan/env

    # Verify installation
    lean --version
    lake --version
    ```

=== "Windows"
    ```powershell
    # Download and run the Windows installer
    # Visit: https://github.com/leanprover/elan/releases
    # Or use Windows Subsystem for Linux (WSL) with the Linux commands above

    # Verify installation
    lean --version
    lake --version
    ```

#### Install UV Package Manager

=== "Linux/macOS"
    ```bash
    # Install UV
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Verify installation
    uv --version
    ```

=== "Windows"
    ```powershell
    # Install via PowerShell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    # Or install via pip
    pip install uv

    # Verify installation
    uv --version
    ```

## 🛠️ Installation Steps

### 1. Clone the Repository

Choose your preferred method to clone the repository:

=== "SSH (Recommended for Contributors)"
    ```bash
    # Clone using SSH
git clone git@github.com:EvolvingLMMs-Lab/lean-runner.git
cd lean-runner
```

=== "HTTPS"
    ```bash
    # Clone using HTTPS
    git clone https://github.com/EvolvingLMMs-Lab/lean-runner.git
    cd lean-runner
    ```

### 2. Set Up Python Environment

Create and activate a Python virtual environment with the required Python version:

=== "Linux/macOS"
    ```bash
    # Create virtual environment with Python 3.12
uv venv --python=3.12

    # Activate the virtual environment
source .venv/bin/activate
    ```

=== "Windows"
    ```powershell
    # Create virtual environment with Python 3.12
    uv venv --python=3.12

    # Activate the virtual environment
    .venv\Scripts\activate
    ```

### 3. Install Server Package

Install the server package in editable mode to enable development:

=== "Standard Installation"
    ```bash
    # Install the server package with all dependencies
    uv pip install -e packages/server
    ```

=== "Development Installation"
    ```bash
    # Install with development dependencies (testing, linting, etc.)
    uv pip install -e "packages/server[dev]"
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

**Note**: The initial build process downloads and compiles Mathlib4 and other dependencies, which can take 10-30 minutes depending on your system.

## 🚀 Running the Server

### Basic Server Startup

Start the server with default settings:

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start the server
lean-server
```

### Advanced Configuration

For production or custom setups, you can specify various options:

```bash
# Set environment variables for configuration
export HOST=0.0.0.0        # Listen on all interfaces
export PORT=8000           # Server port
export CONCURRENCY=32      # Maximum concurrent requests

# Start server with custom settings
lean-server --host=$HOST --port=$PORT --concurrency=$CONCURRENCY
```

### Development Mode

For development, enable auto-reload to automatically restart the server when code changes:

```bash
# Start in development mode with auto-reload
lean-server --host=0.0.0.0 --port=8000 --reload
```

### Command Line Options

The `lean-server` command supports the following options:

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `127.0.0.1` | Host address to bind to |
| `--port` | `8000` | Port number to listen on |
| `--concurrency` | `10` | Maximum number of concurrent proof verifications |
| `--reload` | `False` | Enable auto-reload for development |
| `--config` | `config.yaml` | Path to configuration file |
| `--log-level` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Example Configurations

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
    lean-server --host=0.0.0.0 --port=8000 --concurrency=50 --log-level=INFO
    ```

    **Features:**
    - External access enabled
    - Moderate concurrency
    - Standard logging
    - Balanced performance

=== "High-Performance Setup"
    ```bash
    lean-server --host=0.0.0.0 --port=8000 --concurrency=100 --log-level=WARNING
    ```

    **Features:**
    - Maximum concurrency
    - Minimal logging overhead
    - Optimized for throughput
    - Requires sufficient system resources

## 📁 Configuration File

Create a `config.yaml` file in the project root for persistent configuration:

```yaml
# Server configuration
server:
  host: "0.0.0.0"
  port: 8000
  concurrency: 32

# Lean configuration
lean:
  executable: "/home/user/.elan/bin/lake"
  workspace: "/path/to/lean-runner/playground"
  timeout: 30  # Timeout for proof verification in seconds

# Database configuration
database:
  path: "./lean_server.db"
  timeout: 10

# Logging configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

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
{"status": "healthy", "version": "1.0.0"}
```

### 2. Test Proof Verification

=== "Using curl"
    ```bash
    # Test with a simple proof
    curl -X POST http://localhost:8000/prove/check \
      -H "Content-Type: application/json" \
      -d '{"proof": "theorem test : 1 + 1 = 2 := by norm_num"}'
    ```

=== "Using Python client"
    ```python
    from lean_client import LeanClient

    with LeanClient(base_url="http://localhost:8000") as client:
        result = client.verify(proof="theorem test : 1 + 1 = 2 := by norm_num")
        print(result)
    ```

**Expected response:**
```json
{
  "status": "success",
  "messages": ["Proof verification completed successfully"],
  "proof_id": "abc123..."
}
```

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
