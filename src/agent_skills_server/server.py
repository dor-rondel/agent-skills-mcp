"""FastMCP server for exposing agent skills."""

import re
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("agent-skills")


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from a markdown string.

    Args:
        content: The content of the markdown file.

    Returns:
        A dictionary containing parsed metadata.
    """
    metadata = {}
    # Find frontmatter between the first two --- lines
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)
        for line in frontmatter_text.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip()
    return metadata


def discover_skills(base_dir: str = "resources") -> list[dict[str, str]]:
    """Scan the base directory for SKILL.md files and parse their metadata.

    Args:
        base_dir: Directory to scan for skills.

    Returns:
        A list of dictionaries with skill metadata.
    """
    skills: list[dict[str, str]] = []
    base_path = Path(base_dir)
    if not base_path.exists():
        return skills

    # Recursively find all SKILL.md files
    for skill_file in base_path.glob("**/SKILL.md"):
        # Rel path relative to base_dir, e.g. langgraph/langgraph-project-init/SKILL.md
        rel_path = skill_file.relative_to(base_path)
        parts = rel_path.parts
        if len(parts) >= 3:
            category = parts[0]
            skill_name = parts[1]
            try:
                content = skill_file.read_text(encoding="utf-8")
                metadata = parse_frontmatter(content)
            except Exception:  # pylint: disable=broad-except
                metadata = {}

            skills.append(
                {
                    "name": metadata.get("name", skill_name),
                    "description": metadata.get(
                        "description", "No description provided."
                    ),
                    "category": category,
                    "skill_name": skill_name,
                    "path": str(skill_file),
                }
            )
    # Sort skills by category and name for consistency
    skills.sort(key=lambda x: (x["category"], x["name"]))
    return skills


@mcp.tool()
def list_skills() -> list[dict[str, str]]:
    """List all available agent skills and their metadata.

    Returns:
        A list of dictionaries, each containing:
            - name: The human-readable name of the skill.
            - description: The description of what the skill does.
            - category: The category (e.g. solidity, langgraph).
            - skill_name: The directory identifier of the skill.
            - path: The path to the skill markdown file.
    """
    current_file_path = Path(__file__).resolve()
    repo_root = current_file_path.parent.parent.parent
    resources_dir = repo_root / "resources"
    return discover_skills(str(resources_dir))


@mcp.resource("skills://{category}/{skill_name}")
def get_skill(category: str, skill_name: str) -> str:
    """Get the content of a specific skill by category and skill name.

    Args:
        category: The category of the skill (e.g., solidity, langgraph).
        skill_name: The directory name of the skill (e.g., foundry-project-init).

    Returns:
        The markdown content of the skill file.

    Raises:
        ValueError: If the skill does not exist or access is invalid.
    """
    # Normalize category and skill_name to prevent directory traversal
    category_name = Path(category).name
    skill_dir_name = Path(skill_name).name

    current_file_path = Path(__file__).resolve()
    repo_root = current_file_path.parent.parent.parent
    skill_file = repo_root / "resources" / category_name / skill_dir_name / "SKILL.md"

    if not skill_file.exists():
        raise ValueError(f"Skill not found: {category}/{skill_name}")

    return skill_file.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
