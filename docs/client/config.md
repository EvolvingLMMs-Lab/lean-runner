
# Proof Configuration

The `ProofConfig` object allows you to customize the behavior of the proof verification process. Here are the available options:

- **`all_tactics: bool`** (default: `False`)
    - If `True`, the server will return all tactics executed during the proof, including those from imported libraries.
- **`ast: bool`** (default: `False`)
    - If `True`, the server will include the Abstract Syntax Tree (AST) of the proof in the result.
- **`tactics: bool`** (default: `False`)
    - If `True`, the server will return the tactics used in the main proof.
- **`premises: bool`** (default: `False`)
    - If `True`, the server will return the premises (dependencies) of the proof.
- **`timeout: float`** (default: `300.0`)
    - The maximum time in seconds to wait for the proof verification to complete.
