FROM pufanyi/lean-server:latest

WORKDIR /root/lmms-lean-runner

EXPOSE 8000

CMD ["/root/lmms-lean-runner/.venv/bin/lean-server", "--host", "0.0.0.0", "--port", "8000"]
