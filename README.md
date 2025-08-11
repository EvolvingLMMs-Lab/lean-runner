<div align="center">

<a href="https://lean-runner.vercel.app/">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo/logo-wt-dark.webp">
        <img alt="Lean Runner Logo" src="docs/assets/logo/logo-wt.webp">
    </picture>
</a>

[![Documentation](https://img.shields.io/badge/Documentation-purple?style=flat-square&logo=materialformkdocs)](https://lean-runner.vercel.app/)
[![Lean Server](https://img.shields.io/pypi/v/lean-server?label=Lean%20Server&style=flat-square&color=orange&logo=pypi)](https://pypi.org/project/lean-server/)
[![Lean Runner](https://img.shields.io/pypi/v/lean-runner?label=Lean%20Runner&style=flat-square&color=orange&logo=pypi)](https://pypi.org/project/lean-runner/)
[![Docker](https://img.shields.io/badge/Hub-blue?label=Docker&style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/r/pufanyi/lean-server)

[![Python3.12](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![Lean 4](https://img.shields.io/badge/Lean-4-purple?style=flat-square&logo=lean&logoColor=white)](https://lean-lang.org/doc/reference/4.22.0-rc4/releases/v4.22.0/)
[![Mathlib](https://img.shields.io/badge/Mathlib-v4.22.0--rc4-purple?style=flat-square)](https://github.com/leanprover-community/mathlib4/releases/tag/v4.22.0-rc4)
[![FastAPI](https://img.shields.io/badge/FastAPI-green?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

</div>

## Why Lean-Runner?

- **🚀 Plug & Play**: Get started in minutes with Docker's one-click server setup. Our intuitive client abstracts away complex implementation details, letting you focus on what matters—your Lean proofs.

- **⚡ High Performance**: Leverages REPL-based atomized execution with fully asynchronous, multi-threaded architecture to maximize CPU utilization and throughput.

- **🛡️ Robust & Reliable**: Persistent SQLite logging ensures your work is never lost. Built-in crash recovery and automatic retry mechanisms eliminate the frustration of interrupted workflows.

- **🔄 Flexible Access Patterns**: Choose between synchronous and asynchronous clients depending on your use case—from interactive development to large-scale batch processing.

- **🧠 Smart Caching**: Intelligent content-based hashing ensures identical Lean code is processed only once, dramatically reducing computation time for repeated operations.

- **📊 Data Export & Visualization (Soon)**: Easily export data in various formats (Hugging Face, JSON, XML, Arrow, Parquet) and visualize queries with a simple CLI.

## Getting Started

Check the [quick start](https://lean-runner.vercel.app/quick-start/) guide for detailed instructions on how to get started with Lean-Runner.

## Why Server-Client?

Lean-Runner leverages a powerful Server-Client architecture that smartly places all the complex configuration on the server side, while keeping the client implementation elegantly minimal. We've packaged the entire server using [Docker](https://www.docker.com/), making deployment incredibly straightforward and hassle-free.

![](docs/assets/imgs/overview.webp)

## Why Async?

Lean-Runner's asynchronous architecture uses a **single centralized controller** to manage multiple REPL processes, unlike traditional systems that distribute requests across multiple controllers. This design delivers superior performance through concurrent execution, better resource utilization, and direct communication channels. The centralized approach reduces overhead, and enables intelligent load balancing. This scalable architecture allows you to dynamically add more REPL processes as needed, making it perfect for both interactive development and large-scale batch processing of Lean proofs.

![](docs/assets/imgs/async.webp)

## Project Structure

```text
lean-runner/
├── packages/
│   ├── server/             # FastAPI server implementation
│   │   └── lean_server/
│   │       ├── app/        # API endpoints and server setup
│   │       ├── proof/      # Lean proof execution logic
│   │       ├── manager/    # Proof job management
│   │       ├── config/     # Configuration files and loading
│   │       ├── database/   # SQLite persistence layer
│   │       └── utils/      # Utility functions
│   └── client/             # Python client libraries
│       └── lean_runner/
│           ├── client/     # Sync and async client implementations
│           └── proof/      # Proof data protocol
├── playground/             # Lean workspace with dependencies
└── demo/                   # Example scripts and test files
```


## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

```bibtex
@misc{fanyi2025leanrunner,
  title={Lean-Runner: Deploying High-Performance Lean 4 Server in One Click},
  author={Fanyi Pu, Oscar Qian, Jinghao Guo, Bo Li},
  year={2025},
  publisher={GitHub},
  howpublished={\url{https://github.com/EvolvingLMMs-Lab/lean-runner}},
}
```
