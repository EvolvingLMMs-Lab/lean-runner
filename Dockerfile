# Use the official base image provided in the installation guide
# This image should contain Lean, Python, and necessary GPU drivers.
FROM pufanyi/lean-server:latest

# Set the working directory inside the container
WORKDIR /workspace/lean-server

# Copy all project files to the working directory
COPY . .

# Create a virtual environment and install Python dependencies
# Using 'uv' as specified in the installation guide.
RUN /root/.local/bin/uv venv --python=3.12 && \
    source .venv/bin/activate && \
    /root/.local/bin/uv pip install -e .

# Expose the port the application will run on.
# I will check the config files to determine the correct port.
# Defaulting to 8000 for now, a common port for FastAPI apps.
EXPOSE 8000

# The command to run the application.
# This uses the script defined in pyproject.toml.
CMD ["/bin/bash", "-c", "source .venv/bin/activate && lean-server"]
