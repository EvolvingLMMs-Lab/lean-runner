# Development Roadmap

This page documents the development roadmap and planned features for Lean Server.


-   [ ] **Custom Mathlib Support in Docker**
    -   Support for using custom `mathlib` versions within Docker containers
    -   This would allow users to specify different Mathlib versions for their proofs without rebuilding the entire Docker image
    -   Currently, the server uses a fixed Mathlib version bundled in the Docker image (`pufanyi/lean-server:latest`)
-   [ ] **Data Export Capabilities**
    -   [ ] :simple-huggingface: [Hugging Face Datasets](https://huggingface.co/docs/datasets/en/index) - Export proof verification results to HF Datasets format for ML research
    -   [ ] :simple-json: [JSON](https://www.json.org/json-en.html) / [JSONL](https://jsonlines.org/) - Standard JSON formats for easy integration with other tools
    -   [ ] :fontawesome-solid-file-csv: CSV - Tabular data export for analysis and reporting
    -   [ ] :material-file-excel: Excel - Business-friendly format for sharing results
    -   [ ] :simple-apacheparquet: [Parquet](https://parquet.apache.org/) - Columnar storage format for big data processing
    -   [ ] [Arrow](https://arrow.apache.org/) - In-memory columnar format for high-performance analytics
-   [ ] **Data Visualization**
-   [ ] **Docker Layer Optimization**
    -   Optimize Docker image layering to make `docker pull` operations faster
    -   This will reduce download time when updating to newer versions of the server
    -   Current users need to pull the entire image even for small updates
