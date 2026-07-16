---
name: chromadb-management
description: Use this skill when the user asks to inspect, query, reset, or manage collections inside the ChromaDB vector store container.
---

# ChromaDB Vector Store Management

This skill handles data operations, diagnostics, and API validations for the local ChromaDB service running on port 8000.

## 🛠️ Service Target

- **Host Address:** http://127.0.0.1:8000
- **Data Volume:** Persisted locally at `./chroma_data`

## 🏃‍♂️ Core Commands

### 1. Verify Service Liveness

Check if the ChromaDB server instance is up and responsive to HTTP requests:

```bash
curl -s http://127.0.0.1:8000/api/v1/heartbeat
```

### 2. Inspect Collections via API

Query the database server to view all existing collections and vector indices:

```bash
curl -s http://127.0.0.1:8000/api/v1/collections
```

### 3. Review Container DB Logs

Monitor data ingestion, index updates, or read/write errors directly from the database server instance:

```bash
docker-compose logs chroma
```
