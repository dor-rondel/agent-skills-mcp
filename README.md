# Agent Skills MCP Server

This repository exposes a collection of agent skills (system prompts, guides, and workflows in markdown format) via a Model Context Protocol (MCP) server. By hosting these files as resources and tools, any MCP-compatible coding agent (like Claude Desktop or Cursor) can discover and consume these skills to execute specialized developer tasks.

---

## 📁 Repository Structure

*   `resources/`: Markdown files (`SKILL.md`) organized by category.
    *   `resources/langgraph/`: LangGraph initialization, workflows, and observability.
    *   `resources/solidity/`: Foundry, EVM deployments, and lifecycle.
    *   `resources/docker/`: Ollama, ChromaDB, and container lifecycles.
    *   `resources/frontend/`: Next.js initialization, GLB-to-JSX transformations, and PR preparation.
*   `src/agent_skills_server/`: The FastMCP server application code.
*   `tests/`: Unit test suite.
*   `.gemini/AGENTS.md`: Technical style guides and rules for contributing AI agents.

---

## 🚀 Quick Start

### Prerequisites
Make sure you have [uv](https://github.com/astral-sh/uv) installed:
```bash
curl -LsSf https://astral-sh/uv/install.sh | sh
```

### Installation
Clone the repository and install all dependencies:
```bash
git clone https://github.com/dor-rondel/agent-skills.git
cd agent-skills
make install
```

### Running the Server Locally

#### Development & Testing Mode (MCP Inspector)
FastMCP includes a browser-based inspector for testing tools and resources. To run it:
```bash
uv run fastmcp dev src/agent_skills_server/server.py
```
This command spins up the server and opens the MCP Inspector in your browser (usually at `http://localhost:5173`).

#### Run in Production Mode (stdio)
To run the server ready for an MCP client to communicate via standard I/O:
```bash
uv run fastmcp run src/agent_skills_server/server.py
```

---

## 🔌 Connecting to MCP Clients

You can connect your LLM agent to the server using either:
*   **Option A: Automatic Subprocess (Stdio)**: The client launches the server as a background subprocess when needed. (Recommended, no need to manually keep a server terminal running).
*   **Option B: Persistent Server (SSE/HTTP)**: You manually run the server on a port (`http://127.0.0.1:8000/sse`), and the client connects to it over HTTP.
    *   To run persistently:
        ```bash
        uv run fastmcp run --transport sse --port 8000 src/agent_skills_server/server.py
        ```

---

### Claude Desktop
Add the server definition to your Claude Desktop config file:
*   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Linux**: `~/.config/Claude/claude_desktop_config.json`
*   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Option A: Automatic Subprocess (Stdio)
```json
{
  "mcpServers": {
    "agent-skills": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/agent-skills",
        "run",
        "fastmcp",
        "run",
        "src/agent_skills_server/server.py"
      ]
    }
  }
}
```

#### Option B: Persistent Server (SSE)
```json
{
  "mcpServers": {
    "agent-skills": {
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

---

### Cursor
Go to **Settings** > **Features** > **MCP** and click **+ Add New MCP Server**.

#### Option A: Automatic Subprocess (Stdio)
*   **Name**: `agent-skills`
*   **Type**: `command`
*   **Command**: `uv --directory /absolute/path/to/agent-skills run fastmcp run src/agent_skills_server/server.py`

#### Option B: Persistent Server (SSE)
*   **Name**: `agent-skills`
*   **Type**: `SSE`
*   **URL**: `http://127.0.0.1:8000/sse`

---

### VS Code / Google Antigravity
1. Open the IDE Settings (gear icon in the bottom-left corner).
2. Go to the **Customizations** tab.
3. Click **Open MCP Config** to open `mcp_config.json`.

#### Option A: Automatic Subprocess (Stdio)
Add the configuration under the `mcpServers` key:
```json
{
  "mcpServers": {
    "agent-skills": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/agent-skills",
        "run",
        "fastmcp",
        "run",
        "src/agent_skills_server/server.py"
      ]
    }
  }
}
```

#### Option B: Persistent Server (SSE)
Add the configuration under the `mcpServers` key:
```json
{
  "mcpServers": {
    "agent-skills": {
      "serverUrl": "http://127.0.0.1:8000/sse"
    }
  }
}
```

---


## 🛠️ Development & Quality Controls

This repository enforces strict code quality checks before merging code. You can run all verification tools locally:

*   **Format code**: `make format`
*   **Lint code**: `make lint`
*   **Run unit tests**: `make test`
*   **Spell check**: `make spell`
*   **Run all checks (equivalent to CI)**: `make check`
