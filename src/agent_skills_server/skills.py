"""Skill discovery and metadata parsing utilities for the agent-skills server."""

import re
from pathlib import Path


def get_resources_dir() -> Path:
    """Return the absolute path to the resources/ directory at the repo root.

    Returns:
        The resolved absolute path to the ``resources/`` directory.
    """
    return Path(__file__).resolve().parent.parent.parent / "resources"


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from a markdown string.

    Reads key-value pairs from the YAML block delimited by ``---`` at the
    start of the file. Only simple ``key: value`` pairs are supported.

    Args:
        content: The full text content of the markdown file.

    Returns:
        A dictionary of parsed frontmatter key-value pairs. Returns an empty
        dictionary if no frontmatter block is found.
    """
    metadata: dict[str, str] = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip()
    return metadata


def discover_skills(base_dir: str) -> list[dict[str, str]]:
    """Scan a directory recursively for SKILL.md files and parse their metadata.

    Expects the directory layout::

        <base_dir>/
          <category>/
            <skill-name>/
              SKILL.md

    Args:
        base_dir: Path to the root resources directory to scan.

    Returns:
        A sorted list of skill metadata dictionaries. Each entry contains:

            - ``name``: Human-readable name from frontmatter, or the
              directory name as fallback.
            - ``description``: Description from frontmatter, or a default
              placeholder string.
            - ``category``: The first-level subdirectory (e.g., ``solidity``).
            - ``skill_name``: The second-level subdirectory identifier.
            - ``path``: Absolute path to the SKILL.md file.

        Skills are sorted alphabetically by ``(category, name)``.
    """
    skills: list[dict[str, str]] = []
    base_path = Path(base_dir)
    if not base_path.exists():
        return skills

    for skill_file in base_path.glob("**/SKILL.md"):
        rel_path = skill_file.relative_to(base_path)
        parts = rel_path.parts
        if len(parts) < 3:
            continue

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
                "description": metadata.get("description", "No description provided."),
                "category": category,
                "skill_name": skill_name,
                "path": str(skill_file),
            }
        )

    skills.sort(key=lambda x: (x["category"], x["name"]))
    return skills
