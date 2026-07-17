# Agent Instructions - Agent Skills MCP Server

Welcome! This document outlines the project overview, coding guidelines, and best practices for AI agents contributing to this codebase.

## 📋 Project Overview

This repository has transitioned from a static markdown-based storage of agent skills into a Python-based project. It exposes these skills via a Model Context Protocol (MCP) server powered by `fastmcp`.

*   **Runtime Environment**: Python 3.12+ managed by `uv`.
*   **Dependency Management**: `pyproject.toml` and `uv.lock`.
*   **Code Quality**: Enforced via `ruff`, `pylint`, `mypy`, `codespell`, and `pytest`.
*   **Local Automation**: Run `make check` to run all validation tools locally.

---

## 🛠️ Coding Guidelines & Best Practices

To ensure that the codebase remains clean, maintainable, and passes all local and remote CI checks, please adhere to the following rules:

### 1. Pythonic Code & Type Annotations
*   Write clean, readable, PEP 8-compliant code.
*   **Strict Typing**: Every function signature must have complete type annotations for all parameters and return types. `mypy` will reject untyped or poorly typed code.

### 2. Comprehensive Documentation & Docstrings
*   All modules, classes, and public functions **must** contain detailed docstrings.
*   Use Google-style docstrings. Include descriptions of arguments, returns, and any raised exceptions:
    ```python
    def my_function(param1: str, param2: int) -> bool:
        """Perform a sample operation.

        Args:
            param1: The first parameter description.
            param2: The second parameter description.

        Returns:
            True if successful, False otherwise.
        """
        return True
    ```
*   `pylint` is configured strictly and will penalize missing docstrings or docstring arguments.

### 3. Testing Requirements
*   Any new tool, resource, helper, or command added to the server must be accompanied by comprehensive unit tests in the `tests/` directory.
*   Run tests using `make test`.

### 4. Spelling (codespell)
*   Ensure that code comments, docstrings, variable names, and resource text do not contain spelling errors.
*   Running `make spell` will run `codespell` to catch errors. Configure ignored patterns/words in `pyproject.toml` under `[tool.codespell]` if necessary.

### 5. Vector Store & Local Embeddings
*   Semantic search relies on a local ChromaDB collection persisted in the `.chroma/` directory at the repository root.
*   Embeddings are built using the `all-MiniLM-L6-v2` model running entirely locally on CPU.
*   The index is built lazily during search queries. If you modify any `SKILL.md` documents, the server automatically updates the index. To pre-build or verify the index, trigger a dummy search query via `fastmcp call`.

### 6. Editable Package Installation
*   Always ensure the project package is installed in editable mode (`uv pip install -e .`) in the development environment. This ensures that the FastMCP server launcher and external tools can successfully resolve the `agent_skills_server` package without throwing a `ModuleNotFoundError`.

---

## 📁 Repository Structure

*   `src/agent_skills_server/`: Server source code.
*   `tests/`: Test suite.
*   `resources/`: All skill markdown files, organized by category (e.g., `resources/langgraph/`, `resources/frontend/`).
*   `.chroma/`: Local ChromaDB vector database directory containing the generated embeddings.
