---
name: ollama-model-management
description: Use this skill when the user asks to pull new models, list active models, or check the status of the Ollama engine inside the container.
---

# Ollama Model Management

This skill handles interaction with the Ollama service to update, add, or audit local LLM and embedding models.

## 🛠️ Service Target

- **Host Address:** http://127.0.0.1:11435
- **Default Preloaded Models:** `llama3`, `nomic-embed-text`

## 🏃‍♂️ Core Commands

### 1. List Installed Models

Query the active Ollama engine inside the container to see what weights are already loaded on disk:

```bash
docker exec -it ollama ollama list
```

### 2. Download / Pull a New Model

Instruct the containerized daemon to pull down a new model directly from the Ollama registry:

```bash
docker exec -it ollama ollama pull <model-name>
```

### 3. Check Service Logs

If a model fails to load or download, inspect the execution logs directly from the active service:

```bash
docker-compose logs ollama
```
