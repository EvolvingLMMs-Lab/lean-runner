# API Reference

This document provides a comprehensive reference for all REST API endpoints available in the Lean Server.

!!! info "Base URL"
    All API endpoints are relative to your server's base URL (e.g., `http://localhost:8000`)

## Overview

### What is Lean Proof Configuration?

Many API endpoints accept a ==`config`== parameter for customizing proof verification behavior. This is a JSON string that controls how the Lean theorem prover processes your proof.

!!! example "Basic Configuration Example"
    ```json
    {
      "timeout": 300.0,        // Timeout in seconds (default: 300.0)
      "all_tactics": false,    // Include all tactics in result
      "tactics": false,        // Include tactics in result
      "ast": false,            // Include abstract syntax tree
      "premises": false        // Include premises in result
    }
    ```

!!! note "Configuration Usage"
    - **Simple usage**: Pass `"{}"` for default settings
    - **Custom settings**: Provide JSON string with specific options
    - **All endpoints**: Configuration applies to `/prove/check` and `/prove/submit`

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | float | `300.0` | Maximum processing time in seconds |
| `all_tactics` | boolean | `false` | Include all tactics in the proof result |
| `tactics` | boolean | `false` | Include tactics information in the result |
| `ast` | boolean | `false` | Include abstract syntax tree in the result |
| `premises` | boolean | `false` | Include premises information in the result |

!!! warning "Advanced Configuration"
    ```json
    {
      "timeout": 600.0,        // 10 minutes timeout
      "all_tactics": true,     // Get detailed tactic information
      "tactics": true,         // Include tactics
      "ast": true,             // Include syntax tree
      "premises": true         // Include premises
    }
    ```

### Quick Start Workflow

!!! success "Typical Usage Pattern"
    1. **Choose your approach:**
       - ==Synchronous== (`/prove/check`) - Get immediate results
       - ==Asynchronous== (`/prove/submit` → `/prove/result/{id}`) - For longer proofs
    
    2. **Prepare your configuration:**
       - Start with `"{}"` for simple proofs
       - Use custom config for detailed analysis (tactics, AST, premises)
    
    3. **Submit your proof:**
       - Include both `proof` and `config` parameters
       - Monitor response status codes for errors
    
    4. **Handle results:**
       - Check returned JSON for proof verification status
       - Use proof ID for async result retrieval

### Response Format

Proof verification endpoints return results in the following format:

```json
{
  "success": true,              // Whether the proof was successful
  "status": "finished",         // Status: pending, running, finished, error
  "result": {                   // Detailed result based on config options
    "tactics": [...],           // If tactics: true
    "ast": {...},               // If ast: true
    "premises": [...]           // If premises: true
  },
  "error_message": null         // Error message if status is "error"
}
```

## Health Check

### `GET /health`

Health check endpoint to verify server status and basic information.

=== "Response"
    ```json
    {
      "status": "ok",
      "message": "Lean Server is running",
      "version": "0.0.1"
    }
    ```

=== "cURL Example"
    ```bash
    curl "http://localhost:8000/health"
    ```

**Status Codes:** `200` (Success), `500` (Server Error)

---

## Proof Management

### `POST /prove/check`

Check a Lean proof for correctness synchronously.

!!! note "Content Type"
    This endpoint requires ==`application/x-www-form-urlencoded`== content type.

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `proof` | string | :white_check_mark: | - | The Lean proof code to check |
| `config` | string | :x: | `"{}"` | [Proof configuration](#what-is-lean-proof-configuration) JSON |

=== "Basic cURL Example"
    ```bash
    # Using default configuration
    curl -X POST "http://localhost:8000/prove/check" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "proof=theorem test : 1 + 1 = 2 := by norm_num" \
      -d "config={}"
    ```

=== "Advanced cURL Example"
    ```bash
    # Using custom configuration (longer timeout, detailed output)
    curl -X POST "http://localhost:8000/prove/check" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "proof=theorem complex : ∀ n : ℕ, n + 0 = n := by intro; rfl" \
      -d 'config={"timeout": 600.0, "all_tactics": true, "ast": true}'
    ```

=== "Python Basic Example"
    ```python
    import requests
    
    # Using default configuration
    response = requests.post(
        "http://localhost:8000/prove/check",
        data={
            "proof": "theorem test : 1 + 1 = 2 := by norm_num",
            "config": "{}"
        }
    )
    result = response.json()
    ```

=== "Python Advanced Example"
    ```python
    import requests
    import json
    
    # Using custom configuration for detailed analysis
    config = {
        "timeout": 600.0,       # 10 minutes timeout
        "all_tactics": True,    # Get all tactic details
        "tactics": True,        # Include tactics info
        "ast": True,            # Include syntax tree
        "premises": True        # Include premises
    }
    
    response = requests.post(
        "http://localhost:8000/prove/check",
        data={
            "proof": "theorem complex : ∀ n : ℕ, n + 0 = n := by intro; rfl",
            "config": json.dumps(config)  # Convert dict to JSON string
        }
    )
    result = response.json()
    ```

**Status Codes:** `200` (Success), `500` (Server Error)

---

### `POST /prove/submit`

Submit a Lean proof for asynchronous processing.

!!! tip "Asynchronous Processing"
    This endpoint returns immediately with a proof ID. Use `/prove/result/{proof_id}` to retrieve the result.

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `proof` | string | :white_check_mark: | - | The Lean proof code to submit |
| `config` | string | :x: | `"{}"` | [Proof configuration](#what-is-lean-proof-configuration) JSON |

=== "Basic cURL Example"
    ```bash
    # Submit with default configuration
    curl -X POST "http://localhost:8000/prove/submit" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "proof=theorem test : 1 + 1 = 2 := by norm_num" \
      -d "config={}"
    ```

=== "Advanced cURL Example"
    ```bash
    # Submit with custom timeout and detailed output for complex proofs
    curl -X POST "http://localhost:8000/prove/submit" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "proof=theorem hard_proof : some_complex_statement := by sorry" \
      -d 'config={"timeout": 900.0, "all_tactics": true, "ast": true, "premises": true}'
    ```

=== "Python Basic Example"
    ```python
    import requests
    
    # Submit with default configuration
    response = requests.post(
        "http://localhost:8000/prove/submit",
        data={
            "proof": "theorem test : 1 + 1 = 2 := by norm_num",
            "config": "{}"
        }
    )
    submission_result = response.json()
    proof_id = submission_result.get("proof_id")
    ```

=== "Python Advanced Example"
    ```python
    import requests
    import json
    
    # Submit complex proof with detailed analysis configuration
    config = {
        "timeout": 900.0,        # 15 minutes timeout for complex proofs
        "all_tactics": True,     # Get all tactic details
        "tactics": True,         # Include tactics information
        "ast": True,             # Include abstract syntax tree
        "premises": True         # Include premises information
    }
    
    response = requests.post(
        "http://localhost:8000/prove/submit",
        data={
            "proof": "theorem complex_proof : some_statement := by tactic_sequence",
            "config": json.dumps(config)
        }
    )
    
    submission_result = response.json()
    proof_id = submission_result.get("proof_id")
    print(f"Submitted proof with ID: {proof_id}")
    ```

**Status Codes:** `200` (Success), `502` (Bad Gateway)

---

### `GET /prove/result/{proof_id}`

Retrieve the result of a previously submitted proof.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proof_id` | string | :white_check_mark: | The ID of the submitted proof |

=== "cURL Example"
    ```bash
    curl "http://localhost:8000/prove/result/your-proof-id-here"
    ```

=== "Python Example"
    ```python
    import requests
    
    proof_id = "your-proof-id-here"
    response = requests.get(f"http://localhost:8000/prove/result/{proof_id}")
    result = response.json()
    ```

**Status Codes:** `200` (Success), `404` (Not Found), `500` (Server Error)

---

## Database Operations

### `GET /db/fetch`

Fetch data from the database using SQL queries with efficient batch processing.

!!! warning "Streaming Response"
    This endpoint returns a ==streaming JSON response== with `Content-Disposition: attachment` header.

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | :x: | `"SELECT * FROM proof"` | SQL query to execute |
| `batch_size` | integer | :x: | `100` | Number of records per batch |

=== "cURL Example"
    ```bash
    curl "http://localhost:8000/db/fetch?query=SELECT * FROM proof LIMIT 10&batch_size=50"
    ```

=== "Python Example"
    ```python
    import requests
    
    response = requests.get(
        "http://localhost:8000/db/fetch",
        params={
            "query": "SELECT * FROM proof WHERE created_at > '2025-01-01'",
            "batch_size": 50
        },
        stream=True
    )
    
    # Handle streaming response
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode('utf-8'))
    ```

=== "Response Headers"
    ```
    Content-Type: application/json
    Content-Disposition: attachment; filename=query_results.json
    ```

**Status Codes:** `200` (Success), `500` (Database Error)

---

### `DELETE /db/clean`

Clean the database by removing old proof records and orphaned status entries.

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `seconds` | integer | :x: | `0` | Remove records older than specified seconds |

=== "Response"
    ```json
    {
      "message": "Database cleaned successfully"
    }
    ```

=== "cURL Example"
    ```bash
    # Clean records older than 1 hour (3600 seconds)
    curl -X DELETE "http://localhost:8000/db/clean?seconds=3600"
    ```

=== "Python Example"
    ```python
    import requests
    
    # Clean records older than 24 hours
    response = requests.delete(
        "http://localhost:8000/db/clean",
        params={"seconds": 86400}
    )
    result = response.json()
    print(result["message"])
    ```

**Status Codes:** `200` (Success), `500` (Database Error)

---

## Status Codes Reference

All API endpoints use standard HTTP status codes to indicate the success or failure of requests.

### Success Codes

| Code | Description | Usage |
|------|-------------|--------|
| `200` | OK | Request completed successfully |

### Client Error Codes

| Code | Description | When it occurs |
|------|-------------|----------------|
| `400` | Bad Request | Invalid parameters or malformed request |
| `404` | Not Found | Resource doesn't exist (e.g., proof ID not found) |

### Server Error Codes

| Code | Description | When it occurs |
|------|-------------|----------------|
| `500` | Internal Server Error | Server-side processing error |
| `502` | Bad Gateway | External service error (proof submission failures) |

### Endpoint-Specific Status Codes

| Endpoint | Possible Status Codes |
|----------|----------------------|
| `GET /health` | `200`, `500` |
| `POST /prove/check` | `200`, `500` |
| `POST /prove/submit` | `200`, `502` |
| `GET /prove/result/{proof_id}` | `200`, `404`, `500` |
| `GET /db/fetch` | `200`, `500` |
| `DELETE /db/clean` | `200`, `500` |

---

## Error Handling

!!! failure "Error Response Format"
    All endpoints return errors in a consistent JSON format:

    ```json
    {
      "detail": "Error message description"
    }
    ```

### Error Examples

!!! failure "Common Error Scenarios"
    - ==**400 Bad Request**== - Invalid proof syntax or malformed JSON
    - ==**404 Not Found**== - Proof ID doesn't exist in database
    - ==**500 Server Error**== - Internal processing failure
    - ==**502 Bad Gateway**== - External Lean service unavailable

=== "400 Bad Request"
    ```json
    {
      "detail": "Invalid proof syntax"
    }
    ```

=== "404 Not Found"
    ```json
    {
      "detail": "Proof ID 'invalid-id' not found"
    }
    ```

=== "500 Internal Server Error"
    ```json
    {
      "detail": "Database connection failed"
    }
    ```

!!! tip "Debug Tips"
    - Press ++f12++ to open browser DevTools
    - Use ++ctrl+r++ / ++cmd+r++ to refresh and retry failed requests
    - Check Network tab for detailed HTTP status codes

---

## Additional Resources

!!! note "Further Documentation"
    For more detailed configuration options and server setup, refer to:
    
    - [Configuration Documentation](config.md) - Detailed server configuration
    - [Docker Setup](docker.md) - Container deployment guide  
    - [Source Installation](source.md) - Build from source instructions
    
    **Useful keyboard shortcuts:**
    
    - ++ctrl+shift+p++ - Open command palette  
    - ++ctrl+space++ - Trigger autocomplete
    - ++ctrl+/++ - Toggle line comment
