# Running with Docker

This document explains how to run the `lmms-lean-server` using Docker.

## For End-Users: Run with a Single Command

If you have Docker installed, you can download and run the `lmms-lean-server` with a single command. This will pull the pre-built image from Docker Hub and start the server.

To run the server on port `8000`, execute the following command:

```sh
docker run -d -p 8000:8000 --name lean-server-container your-dockerhub-username/lean-runner
```

**Note:** Please replace `your-dockerhub-username/lean-runner` with the actual image name on Docker Hub.

- `-d`: Runs the container in the background.
- `-p 8000:8000`: Maps port `8000` on your machine to port `8000` in the container. You can change the first `8000` to any other port you prefer (e.g., `-p 8080:8000`).
- `--name lean-server-container`: Assigns a convenient name to your container.

The server will be accessible at `http://localhost:8000` (or your chosen port).

## For Developers: Build and Publish the Image

As a developer, you will need to build and publish the image to a container registry like Docker Hub for others to use.

### 1. Build the Image

In the project's root directory (where the `Dockerfile` is located), run the build command:

```sh
docker build -t your-dockerhub-username/lean-runner .
```

- Replace `your-dockerhub-username` with your Docker Hub username.
- The `.` at the end specifies the current directory as the build context.

### 2. (Optional) Run Locally for Testing

Before publishing, you can test the image locally:

```sh
docker run -d -p 8000:8000 your-dockerhub-username/lean-runner
```

### 3. Publish the Image

First, log in to your Docker Hub account:

```sh
docker login
```

Then, push the image to Docker Hub:

```sh
docker push your-dockerhub-username/lean-runner
```

Once pushed, other users can run the server with the single `docker run` command as described above.
