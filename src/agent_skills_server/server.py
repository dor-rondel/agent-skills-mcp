"""FastMCP server for exposing agent skills as MCP tools and resources."""

from pathlib import Path

from fastmcp import FastMCP

from agent_skills_server.indexer import (
    get_or_create_collection,
    search_skills_in_collection,
)
from agent_skills_server.skills import (
    discover_skills,
    get_resources_dir,
    parse_frontmatter,
)

mcp = FastMCP("agent-skills")


@mcp.tool()
def list_skills() -> list[dict[str, str]]:
    """List all available agent skills and their metadata.

    Scans the ``resources/`` directory for ``SKILL.md`` files and returns
    parsed metadata for every discovered skill. Use this tool to orient
    yourself on what skills exist before fetching their content directly.

    Returns:
        A sorted list of skill metadata dictionaries, each containing:

            - ``name``: Human-readable name of the skill.
            - ``description``: Short description of what the skill does.
            - ``category``: Category directory (e.g., ``solidity``,
              ``langgraph``).
            - ``skill_name``: Directory identifier of the skill.
            - ``path``: Absolute path to the SKILL.md file.
    """
    return discover_skills(str(get_resources_dir()))


@mcp.tool()
def search_skills(query: str, n_results: int = 3) -> list[dict[str, str]]:
    """Search for skills semantically similar to a natural-language query.

    Uses a local ChromaDB vector store with ``all-MiniLM-L6-v2`` sentence
    embeddings to find skills whose content best matches the intent of the
    query. The index is built lazily on first call and refreshed automatically
    when the number of skill files changes.

    Prefer this tool over ``list_skills`` when you have a specific question or
    task and want the most relevant skill without scanning all 13+ entries.

    Args:
        query: A natural-language description of what you are looking for.
            Example: ``"deploy a smart contract to a testnet and verify it"``
        n_results: Maximum number of ranked results to return. Defaults to 3.

    Returns:
        A ranked list of matching skill dictionaries (best match first), each
        containing:

            - ``name``: Human-readable skill name.
            - ``category``: Skill category.
            - ``skill_name``: Directory identifier of the skill.
            - ``description``: Short description of the skill.
            - ``distance``: Cosine distance score (lower = more similar).
    """
    collection = get_or_create_collection()
    return search_skills_in_collection(collection, query, n_results)


@mcp.resource("skills://{category}/{skill_name}")
def get_skill(category: str, skill_name: str) -> str:
    """Get the full markdown content of a specific skill.

    Args:
        category: The category of the skill (e.g., ``solidity``,
            ``langgraph``).
        skill_name: The directory name of the skill (e.g.,
            ``foundry-project-init``).

    Returns:
        The full markdown content of the SKILL.md file.

    Raises:
        ValueError: If the skill does not exist or the path is invalid.
    """
    # Normalise inputs to prevent directory traversal attacks
    category_name = Path(category).name
    skill_dir_name = Path(skill_name).name

    skill_file = get_resources_dir() / category_name / skill_dir_name / "SKILL.md"
    if not skill_file.exists():
        raise ValueError(f"Skill not found: {category}/{skill_name}")

    return skill_file.read_text(encoding="utf-8")


# Re-export helpers so existing tests that import from server still work
__all__ = [
    "mcp",
    "list_skills",
    "search_skills",
    "get_skill",
    # Helpers surfaced for testing convenience
    "discover_skills",
    "parse_frontmatter",
]

if __name__ == "__main__":
    mcp.run()
