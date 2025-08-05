# Lean Server Monorepo

This repository is a monorepo for the Lean Server project, containing the server application and its corresponding Python client.

## 📦 Packages

This repository contains the following independent packages:

-   `packages/server`: The core FastAPI server that exposes the Lean prover via a REST API.
-   `packages/client`: A Python client library (`lean-client`) for easily interacting with the server's API.

## 🚀 Getting Started

The recommended way to work on this project is by using the included [Dev Container](https://code.visualstudio.com/docs/devcontainers/containers) configuration.

### Prerequisites

-   [Docker](https://www.docker.com/products/docker-desktop/)
-   [VS Code](https://code.visualstudio.com/) or [Cursor](https://cursor.sh/)
-   [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed in your editor.

### Development Workflow

1.  **Open in Container**:
    -   Clone this repository.
    -   Open the root folder in VS Code or Cursor.
    -   A notification will appear asking to "Reopen in Container". Click it.

2.  **Install Dependencies**:
    -   Once the Dev Container is running, open a new terminal (`Ctrl+` `).
    -   Install both packages in editable mode using `uv`:
      ```bash
      uv pip install -e packages/server -e packages/client
      ```

3.  **Run the Services**:
    -   **Start the Server**: In a terminal, run the server:
      ```bash
      lean-server
      ```
      This command is available because it's registered as a script in `packages/server/pyproject.toml`.

    -   **Test with the Client**: In a separate terminal, you can run Python scripts to test the client, or use the example from the `packages/client` README.

This setup allows you to modify both server and client code and see the changes reflected immediately.
