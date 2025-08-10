# Development Roadmap

This page documents the development roadmap and planned features for Lean Server.

-   [ ] **Custom Mathlib Support in Docker**
    -   Support for using custom `mathlib` versions within Docker containers
    -   This would allow users to specify different Mathlib versions for their proofs without rebuilding the entire Docker image
    -   Currently, the server uses a fixed Mathlib version ([:material-tag: v4.22.0-rc4](https://github.com/leanprover-community/mathlib4/releases/tag/v4.22.0-rc4)) bundled in the Docker image
-   [ ] **[`config.yaml`](../server/config.md) file support for Docker server**
-   [ ] **Lean Output Result Processing**
    -   [ ] Parse related results
    -   [ ] Support proof simplification
-   [ ] **Data Export Capabilities**
    -   [ ] :simple-huggingface: [Hugging Face Datasets](https://huggingface.co/docs/datasets/en/index)
    -   [ ] :simple-json: [JSON](https://www.json.org/json-en.html) / [JSONL](https://jsonlines.org/)
    -   [ ] :fontawesome-solid-file-csv: CSV
    -   [ ] :material-file-excel: Excel
    -   [ ] :simple-apacheparquet: [Parquet](https://parquet.apache.org/)
    -   [ ] [Arrow](https://arrow.apache.org/)
-   [ ] **Data Visualization**
-   [ ] **Docker Layer Optimization**
    -   Optimize Docker image layering to make `docker pull` operations faster
    -   This will reduce download time when updating to newer versions of the server
    -   Current users need to pull the entire image even for small updates
