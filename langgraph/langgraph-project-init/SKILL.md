---
name: langgraph-project-init
description: Use this skill when initializing a brand new Python LangGraph project from scratch. Covers installing uv, bootstrapping directories, generating the Makefile, configuring LangGraph Studio, and setting up the GitHub Actions CI workflow.
---

# LangGraph Python Project Initialization & CI Setup

This skill provides step-by-step instructions for scaffolding a new LangGraph project using `uv` and setting up both local task runners and automated remote CI pipelines.

## 🏃‍♂️ Step-by-Step Initialization Workflow

### 1. Initialize the Directory & Environment

Create the project folder structure, including the hidden GitHub workflows path, and initialize a new `uv` environment:
mkdir -p langgraph-agent/src langgraph-agent/tests langgraph-agent/scripts langgraph-agent/.github/workflows
cd langgraph-agent
uv init

### 2. Add LangGraph & Core Dependencies

Install the required production packages and local quality tools directly into your lockfile:
uv add langgraph langchain-openai dotenv
uv add --dev ruff pylint mypy pytest codespell

### 3. Generate the Standard Makefile

Write the unified `Makefile` into the root directory to handle linting, formatting, tests, and graph generation:

```
.PHONY: install format lint test graph spell check clean

    PYTHON ?= uv run python
    SRC_DIR := src
    TEST_DIR := tests

    install:
    	uv sync

    format:
    	uv run ruff format .

    lint:
    	uv run ruff check .
    	uv run pylint $(SRC_DIR)
    	uv run mypy $(SRC_DIR)

    test:
    	uv run pytest $(TEST_DIR)

    graph:
    	PYTHONPATH=. uv run python scripts/generate_graph.py

    spell:
    	uv run codespell .

    check:
    	uv run ruff format --check .
    	uv run ruff check .
    	uv run pylint $(SRC_DIR)
    	uv run mypy $(SRC_DIR)
    	uv run pytest $(TEST_DIR)
    	uv run codespell .

    clean:
    	find . -type d -name "__pycache__" -exec rm -rf {} +
    	find . -type f -name "*.py[cod]" -delete
    	find . -type f -name ".coverage" -delete
    	rm -rf .pytest_cache
    	rm -rf .ruff_cache
    	rm -rf .mypy_cache
    	rm -rf .venv
```

### 4. Configure LangGraph Studio

Create a standard `langgraph.json` file so the workspace instantly mounts to the LangGraph visual development desktop application or server:

```
{
"dependencies": ["."],
"graphs": {
"agent": "./src/agent.py:graph"
},
"env": ".env"
}
```

### 5. Establish GitHub Actions CI Workflow

Inject the continuous integration yaml block into your workspace to automatically run tests and code validation on every pull request to `main` or `master` in .github/workflows/ci.yml

```
name: CI

    on:
      pull_request:
        branches: [ main, master ]

    jobs:
      check:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - name: Install uv
            uses: astral-sh/setup-uv@v5
            with:
              enable-cache: true
              version: "latest"

          - name: Set up Python
            run: uv python install 3.12

          - name: Install dependencies
            run: make install

          - name: Run checks
            run: make check
```

---

## 🛠️ Verification Run

Always execute an environment-wide check directly following initialization to ensure everything passes locally before pushing the workspace to GitHub:

```bash
make install
make check
```
