# Configuration Management

This directory contains configuration files for the Lean Runner Server.

## Configuration Files

- `default.yaml` - Default configuration (should not be modified)
- `example.yaml` - Example custom configuration template

## Usage

### Using Default Configuration

```bash
# Run with built-in defaults
./server

# Show current configuration
./server --show-config
```

### Using Custom Configuration

```bash
# Create your custom config based on example
cp configs/example.yaml my-config.yaml

# Edit my-config.yaml as needed
# ...

# Run with custom config
./server --config=my-config.yaml
```

### Command Line Overrides

Command line flags have the highest priority and will override any config file values:

```bash
# Override specific values
./server --config=my-config.yaml --port=8080 --host=0.0.0.0 --log-level=debug

# Show final configuration after overrides
./server --config=my-config.yaml --port=8080 --show-config
```

### Environment Variables

You can also use environment variables with the `LEAN_RUNNER_` prefix:

```bash
export LEAN_RUNNER_SERVER_PORT=8080
export LEAN_RUNNER_SERVER_HOST=0.0.0.0
export LEAN_RUNNER_LOGGER_LEVEL=debug
./server
```

## Configuration Priority (highest to lowest)

1. Command line flags
2. Environment variables
3. Custom config file
4. Default config file
5. Built-in defaults

## Available Configuration Options

See `default.yaml` for all available configuration options and their descriptions.

## For Distributed Systems

This configuration system is designed to work well in distributed environments:

- **Environment variable support** for containerized deployments
- **File-based config** for config maps in Kubernetes
- **CLI override support** for dynamic deployment scenarios
- **Validation** to catch configuration errors early
- **Structured logging** for better observability

For production deployments, consider:
- Using environment variables for sensitive values
- Mounting config files as read-only volumes
- Using config management tools like Helm for templating
- Implementing config reloading for zero-downtime updates (future enhancement)
