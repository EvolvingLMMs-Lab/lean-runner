# Client Library Overview

Welcome to the `lean-runner` client library documentation. This library provides a powerful and flexible Python interface for interacting with the Lean Runner server, allowing you to programmatically verify Lean proofs.

The client is designed to be intuitive and supports both simple synchronous operations and high-performance asynchronous workflows, making it suitable for a wide range of applications, from simple scripts to complex, concurrent systems.

## Getting Started

First, make sure you have the library installed. If not, head over to the installation guide.

- **[Installation](./install.md)**: How to install the client library using `pip` or from source.

## Core Features

The client library offers several ways to verify proofs, catering to different needs.

- **[Simple Query](./simple-query.md)**: The most straightforward way to verify a single proof. The `verify` method sends a proof and waits for the result, making it perfect for quick checks and simple use cases.

- **[Asynchronous Submission and Retrieval](./submit-get-result.md)**: Ideal for long-running proofs. The `submit` method sends a proof to the server and immediately returns a job ID. You can then use the `get_result` method to fetch the outcome at a later time, without blocking your application.

- **[Bulk Verification](./verify-all.md)**: The most efficient way to handle a large number of proofs. The `verify_all` method processes an entire collection of proofs concurrently, yielding results as they become available. This is highly recommended for batch processing tasks.

## Customization

You can fine-tune the verification process to get the exact information you need.

- **[Proof Configuration](./config.md)**: Learn how to use the `ProofConfig` object to control aspects of the verification, such as enabling Abstract Syntax Tree (AST) output, collecting tactics, and setting timeouts.

## Sync vs. Async

All features are available in two flavors:

- **`LeanClient`**: A synchronous client that is easy to use and works well in standard Python scripts.
- **`AsyncLeanClient`**: An asynchronous client built on `httpx` and `asyncio` for high-performance, non-blocking I/O. It's the best choice for concurrent applications.

Each guide provides examples for both clients, so you can choose the one that best fits your programming style.
