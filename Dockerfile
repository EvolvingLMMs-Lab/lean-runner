# Use a base image with Python and Git
FROM python:3.11-slim

# Install git and curl for version control and downloads
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/get/lists/*

# Install elan (Lean toolchain manager) and common build tools
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
ENV PATH="/root/.elan/bin:${PATH}"

# Install uv
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy dependency definition files first to leverage Docker cache
COPY pyproject.toml uv.lock* ./
COPY packages/server/pyproject.toml ./packages/server/
COPY playground/lake-manifest.json playground/lakefile.toml playground/lean-toolchain ./playground/
COPY playground/lakefile.lean ./playground/

# Install python dependencies
RUN uv pip install -e packages/server

# Build the Lean dependencies in the playground directory
# This is done after python deps to ensure lean is available from the package
RUN cd playground && lake build

# Copy the rest of the project source code
COPY . .

# Expose the default port for the server
EXPOSE 8000

# The command to run the server
# The user can override the port and other options via docker run
CMD ["lmms-lean-server", "--port", "8000"]
