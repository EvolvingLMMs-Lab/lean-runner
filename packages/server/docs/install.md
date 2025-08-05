# Installation

```bash
docker create --gpus all --net=host --shm-size="50g" --cap-add=SYS_ADMIN -v .:/workspace/lean-server --name lean-server pufanyi/lean-server:latest sleep infinity
docker start lean-server
docker exec -it lean-server zsh
cd /workspace/lean-server/
uv venv --python=3.12
source .venv/bin/activate
uv pip install -e .
```

Common error:

```plain
Error response from daemon: could not select device driver "" with capabilities: [[gpu]]
Error: failed to start containers: verl
```

The reason is that the NVIDIA Container Toolkit is not [installed](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (check with `dpkg -l | grep nvidia-container-toolkit`). If you are running without root, remember to check the [rootless mode](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#rootless-mode) during configuration.
