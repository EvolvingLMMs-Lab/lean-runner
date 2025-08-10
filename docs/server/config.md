# Configuration

The Lean Runner server can be configured through both command-line arguments and a YAML configuration file. Command-line arguments will always take precedence over the configuration file.

## Command-line Arguments

You can launch the server with the following command-line arguments:

| Argument | Default Value | Description |
|---|---|---|
| `--host` | `0.0.0.0` | The host to bind the server to. |
| `--port` | `8000` | The port to run the server on. |
| `--concurrency` | `32` | Maximum number of concurrent Lean worker threads. |
| `--config` | `default` | Path to a custom YAML configuration file. If not provided, the default configuration is used. |
| `--lean-workspace`| `default` | Path to the Lean workspace. Overrides the `workspace` value in the config file. |
| `--log-level` | `INFO` | Set the logging level. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |

## Configuration File

You can also use a YAML file to configure the server. By default, the server looks for `default_config.yaml`. You can specify a custom configuration file using the `--config` argument.

!!! info
    Using a custom configuration file is primarily intended for when you are running the server from the source code. Support for custom configuration files within a Docker environment is on our [roadmap](../dev/todos.md) and will be implemented in a future release.

A custom configuration file will be deeply merged with the default configuration. This means if you don't specify an option in your custom file, the value from `default_config.yaml` will be used.

The configuration is structured into three main sections: `lean`, `sqlite`, and `logging`.

### `lean`

This section configures the Lean environment.

| Key | Type | Description |
|---|---|---|
| `executable` | string | The absolute path to the `lake` executable. |
| `workspace` | string | The absolute path to the Lean project workspace. |
| `concurrency` | integer | The maximum number of concurrent Lean processes. This can be overridden by the `--concurrency` command-line argument. |

### `sqlite`

This section configures the SQLite database connection.

| Key | Type | Description |
|---|---|---|
| `database_path` | string | The path to the SQLite database file. |
| `timeout` | integer | The connection timeout in seconds. |

### `logging`

This section configures the server's logging behavior using Python's `logging.config` dictionary schema.

!!! tip
    You can customize handlers, formatters, and log levels for different parts of the application. For more details, refer to the [Python logging documentation](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details).

## Default Configuration

Here is the default configuration file:

```yaml title="packages/server/lean_server/config/default_config.yaml"
lean:
  executable: /root/.elan/bin/lake
  workspace: /app/lean-runner/playground
  lean_timeout: 300
sqlite:
  database_path: /app/database/lean_server.db
  timeout: 10
logging:
  version: 1
  disable_existing_loggers: false
  handlers:
    default:
      class: "rich.logging.RichHandler"
      level: "INFO"
      rich_tracebacks: true
      tracebacks_word_wrap: false
  loggers:
    lean_server:
      handlers:
        - "default"
      level: "INFO"
    uvicorn:
      handlers:
        - "default"
      level: "INFO"
      propagate: false
    uvicorn.error:
      handlers:
        - "default"
      level: "INFO"
      propagate: false
    uvicorn.access:
      handlers:
        - "default"
      level: "INFO"
      propagate: false
```
