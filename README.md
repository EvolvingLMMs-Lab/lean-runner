# Lean Server Monorepo

This repository is a monorepo containing multiple related packages for the Lean Server project.

## Directory Structure

-   `packages/`: Contains all the independent, publishable packages.
    -   `lean-server/`: The main server application.
    -   `lean-client/`: (Placeholder for the future client library)
-   `.devcontainer/`: Contains the configuration for the VS Code / Cursor Dev Container.
-   `docker-compose.yml`: Used to orchestrate the services for local development.

## Development

To get started with local development, open this folder in VS Code or Cursor with the "Dev Containers" extension installed and click "Reopen in Container".

This will launch a fully configured development environment using Docker.
