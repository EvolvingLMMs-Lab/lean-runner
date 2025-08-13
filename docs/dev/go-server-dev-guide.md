# Go Server Development Guide

This document provides instructions for running and building the Go server in a local environment.

## Prerequisites

- Go programming environment is installed (version 1.20 or higher).
- Project dependencies are synchronized via `go mod tidy`.

## Running the Server (Development Mode)

During development, you can use the `go run` command to run the server directly without first building a binary. This method speeds up iteration.

1.  **Switch to the server directory:**
    ```bash
    cd server
    ```

2.  **Run the server:**
    The `main` package is located in the `cmd/server` directory. Run the following command from the `server` directory:
    ```bash
    go run ./cmd/server
    ```

The server should now be running and listening on the configured port. You will see log output in your terminal.

## Building the Server (Production Mode)

To build an optimized binary for a production environment, use the `go build` command.

1.  **Switch to the server directory:**
    ```bash
    cd server
    ```

2.  **Build the binary:**
    ```bash
    go build -o ../bin/lean_server ./cmd/server
    ```
    This command does the following:
    - `-o ../bin/lean_server`: Names the output binary `lean_server` and places it in the `bin` directory under the project root. If the `bin` directory does not exist, you will need to create it first (`mkdir bin`).
    - `./cmd/server`: Specifies the path to the `main` package to be built.

3.  **Run the built server:**
    Run from the project root directory:
    ```bash
    ./bin/lean_server
    ```
