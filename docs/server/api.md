# API Reference

This document provides a comprehensive reference for all RESTful API endpoints available in the Lean Prover Server.

!!! info "Base URL"
    All API endpoints are relative to your server's base URL (e.g., `http://localhost:8000`).

## Endpoints

### Health Check

#### `GET /health`

Verifies the server's operational status and retrieves basic information.

**Responses**
- `200 OK`: Server is running.
- `500 Internal ServerError`: Server-side processing error.

**Success Response** `200 OK`
```json
{
  "status": "ok",
  "message": "Lean Server is running",
  "version": "0.0.1"
}
```

**cURL Example**
```bash
curl "http://localhost:8000/health"
```

### Proof Verification

#### `POST /prove/check`

Synchronously verifies a Lean proof for correctness.

!!! note "Content-Type"
    This endpoint requires `application/x-www-form-urlencoded`.

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `proof` | `string` | Yes | - | The Lean proof code to check. |
| `config` | `string` | No | `{}` | A JSON string to configure the proof checking process. See [Proof Configuration](#proof-configuration) for details. |

**Responses**
- `200 OK`: Verification finished.
- `500 Internal Server Error`: Server-side processing error.

**Success Response** `200 OK`
```json
{
  "success": true,
  "status": "finished",
  "result": { ... },
  "error_message": null
}
```

**cURL Example**
```bash
curl -X POST "http://localhost:8000/prove/check" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "proof=theorem test : 1 + 1 = 2 := by norm_num" \
  -d "config={}"
```

**Python Example**
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/prove/check",
    data={
        "proof": "theorem test : 1 + 1 = 2 := by norm_num",
        "config": json.dumps({"timeout": 600.0})
    }
)
print(response.json())
```

#### `POST /prove/submit`

Submits a Lean proof for asynchronous processing and returns a unique `proof_id`.

!!! tip "Asynchronous Processing"
    Use `GET /prove/result/{proof_id}` to retrieve the verification result later.

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `proof` | `string` | Yes | - | The Lean proof code to submit. |
| `config` | `string` | No | `{}` | A JSON string to configure the proof checking process. See [Proof Configuration](#proof-configuration) for details. |

**Responses**
- `200 OK`: Proof submitted successfully.
- `502 Bad Gateway`: Error during proof submission.

**Success Response** `200 OK`
```json
{
  "proof_id": "your-unique-proof-id"
}
```

**cURL Example**
```bash
curl -X POST "http://localhost:8000/prove/submit" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "proof=theorem hard_proof : some_complex_statement := by sorry" \
  -d 'config={"timeout": 900.0}'
```

**Python Example**
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/prove/submit",
    data={
        "proof": "theorem complex_proof : some_statement := by tactic_sequence",
        "config": json.dumps({"timeout": 900.0})
    }
)
proof_id = response.json().get("proof_id")
print(f"Submitted proof with ID: {proof_id}")
```

#### `GET /prove/result/{proof_id}`

Retrieves the result of a previously submitted asynchronous proof.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proof_id`| `string` | Yes | The unique ID of the submitted proof. |

**Responses**
- `200 OK`: Result retrieved successfully.
- `404 Not Found`: The specified `proof_id` does not exist.
- `500 Internal Server Error`: Server-side processing error.

**Success Response** `200 OK`
```json
{
  "success": true,
  "status": "finished",
  "result": { ... },
  "error_message": null
}
```

**cURL Example**
```bash
curl "http://localhost:8000/prove/result/your-proof-id-here"
```

**Python Example**
```python
import requests

proof_id = "your-proof-id-here"
response = requests.get(f"http://localhost:8000/prove/result/{proof_id}")
print(response.json())
```

### Database Management

#### `GET /db/fetch`

Fetches records from the database using an SQL query and streams the results.

!!! warning "Streaming Response"
    This endpoint returns a streaming JSON response with a `Content-Disposition: attachment` header, making it suitable for large datasets.

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | `string` | No | `SELECT * FROM proof` | The SQL query to execute. |
| `batch_size`| `integer`| No | `100` | The number of records to fetch per batch. |

**Responses**
- `200 OK`: Query executed successfully.
- `500 Internal Server Error`: Database error.

**cURL Example**
```bash
curl "http://localhost:8000/db/fetch?query=SELECT * FROM proof LIMIT 10&batch_size=5"
```

**Python Example**
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

for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        print(chunk.decode('utf-8'))
```

#### `DELETE /db/clean`

Cleans the database by removing proof records older than a specified time.

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `seconds` | `integer`| No | `0` | Removes records older than this many seconds. |

**Responses**
- `200 OK`: Database cleaned successfully.
- `500 Internal Server Error`: Database error.

**Success Response** `200 OK`
```json
{
  "message": "Database cleaned successfully"
}
```

**cURL Example**
```bash
# Clean records older than 1 hour (3600 seconds)
curl -X DELETE "http://localhost:8000/db/clean?seconds=3600"
```

**Python Example**
```python
import requests

# Clean records older than 24 hours (86400 seconds)
response = requests.delete(
    "http://localhost:8000/db/clean",
    params={"seconds": 86400}
)
print(response.json())
```

## Data Structures

### Proof Configuration

The `config` parameter is a JSON string used to customize proof verification.

**Default Configuration**
```json
{
  "timeout": 300.0,
  "all_tactics": false,
  "tactics": false,
  "ast": false,
  "premises": false
}
```

**Options**

| Option | Type | Default | Description |
|-------------|---------|---------|-------------------------------------------|
| `timeout` | `float` | `300.0` | Maximum processing time in seconds. |
| `all_tactics`| `boolean`| `false` | Include all tactics in the proof result. |
| `tactics` | `boolean`| `false` | Include tactics information in the result. |
| `ast` | `boolean`| `false` | Include the abstract syntax tree in the result. |
| `premises` | `boolean`| `false` | Include premises information in the result. |

### Proof Result

The proof verification endpoints (`/prove/check` and `/prove/result/{proof_id}`) return a JSON object with the following structure.

**Result Object**
```json
{
  "success": true,
  "status": "finished",
  "result": {
    "tactics": [],
    "ast": {},
    "premises": []
  },
  "error_message": null
}
```

**Fields**

| Field | Type | Description |
|---------------|---------|----------------------------------------------------------|
| `success` | `boolean` | `true` if the proof was successful, otherwise `false`. |
| `status` | `string` | The current status: `pending`, `running`, `finished`, or `error`. |
| `result` | `object` | Contains detailed results based on the `config` options. |
| `error_message`| `string` | An error message if the `status` is `error`. |

## Error Handling

API errors are returned in a consistent JSON format.

**Error Response**
```json
{
  "detail": "A descriptive error message."
}
```

**Common Status Codes**

| Code | Description | Reason |
|------|---------------------------|--------------------------------------------------|
| `400` | Bad Request | Invalid parameters or malformed request body. |
| `404` | Not Found | The requested resource (e.g., a `proof_id`) does not exist. |
| `500` | Internal Server Error | An unexpected error occurred on the server. |
| `502` | Bad Gateway | The server encountered an error with an external service. |
