---
title: Home
---

<style>
  .md-typeset h1 {
    display: none;
  }
</style>

![](assets/logo/logo-wt-dark.webp#only-dark)
![](assets/logo/logo-wt.webp#only-light)

<div align="center" markdown>

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=flat-square&logo=github)](https://github.com/EvolvingLMMs-Lab/lean-runner)
[![Lean Server](https://img.shields.io/pypi/v/lean-server?label=Lean%20Server&style=flat-square&color=orange&logo=pypi)](https://pypi.org/project/lean-server/)
[![Lean Runner](https://img.shields.io/pypi/v/lean-runner?label=Lean%20Runner&style=flat-square&color=orange&logo=pypi)](https://pypi.org/project/lean-runner/)
[![Docker](https://img.shields.io/badge/Hub-blue?label=Docker&style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/r/pufanyi/lean-server)

[![Python3.12](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![Lean 4](https://img.shields.io/badge/Lean-4-purple?style=flat-square&logo=lean&logoColor=white)](https://lean-lang.org/doc/reference/4.22.0-rc4/releases/v4.22.0/)
[![Mathlib](https://img.shields.io/badge/Mathlib-v4.22.0--rc4-purple?style=flat-square)](https://github.com/leanprover-community/mathlib4/releases/tag/v4.22.0-rc4)
[![FastAPI](https://img.shields.io/badge/FastAPI-green?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

<br/>

</div>

<div class="grid cards" markdown>

-   :package: __Plug & Play__

    ---

    Get started in minutes. Docker provides one-click server setup, and the simple client abstracts away implementation details.

    [:octicons-arrow-right-24: Quick Start](quick-start.md)

-   :zap: __Efficient__

    ---

    Fully asynchronous and multi-threaded architecture to maximize CPU utilization.

-   :shield: __Reliable__

    ---

    All logs are persistently stored in a SQLite database for easy access. Say goodbye to the frustration of crashes and re-runs.

-   :gear: __Flexible__

    ---

    Supports both synchronous and asynchronous access patterns to fit your needs.

-   :recycle: __Smart Caching (Soon)__

    ---

    Identical Lean code is only processed once, thanks to smart hashing. Say goodbye to the hassle of configuring continual runs.

-   :bar_chart: __Data Export & Visualization (Soon)__

    ---

    Easily export data in various formats (Hugging Face, JSON, XML, Arrow, Parquet) and visualize queries with a simple CLI.

</div>

!!! quote "Citation"
    ```bibtex
    @misc{fanyi2025leanrunner,
        title={Lean-Runner: Deploying High-Performance Lean 4 Server in One Click},
        author={Fanyi Pu, Oscar Qian, Bo Li},
        year={2025},
        publisher={GitHub},
        howpublished={\url{https://github.com/EvolvingLMMs-Lab/lean-runner}},
    }
    ```
