---
name: docker-lifecycle
description: Use this skill when the user asks to start, stop, restart, or check the status of the local Docker container infrastructure.
---

# Docker Infrastructure Lifecycle Management

This skill handles booting, tearing down, and inspecting the local development infrastructure stack containing Ollama and ChromaDB.

## 🏃‍♂️ Core Commands

### 1. Boot Environment

Spin up all services in detached background mode. This will automatically execute the entrypoint script to verify and pull required models:

```bash
docker-compose up -d
```

### 2. Shut Down Environment

Stop and remove all running containers in the stack without breaking persistent data volumes:

```bash
docker-compose down
```

### 3. Inspect Service Status

Check the logs or health status of active containers to ensure Ollama and ChromaDB are operational:

```bash
docker-compose ps
docker-compose logs -f
```
