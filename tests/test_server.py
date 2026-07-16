"""Tests for the FastMCP server."""

import pytest
from agent_skills_server.server import (
    get_skill,
    list_skills,
    parse_frontmatter,
)


def test_parse_frontmatter():
    """Test the YAML frontmatter parser."""
    content = "---\nname: my-skill\ndescription: A test skill\n---\n# Content"
    meta = parse_frontmatter(content)
    assert meta == {"name": "my-skill", "description": "A test skill"}

    content_no_fm = "# Content without frontmatter"
    meta_no_fm = parse_frontmatter(content_no_fm)
    assert meta_no_fm == {}


def test_list_skills():
    """Test the list_skills tool function."""
    skills = list_skills()
    assert isinstance(skills, list)
    assert len(skills) > 0

    # Verify keys in the first skill
    skill = skills[0]
    assert "name" in skill
    assert "description" in skill
    assert "category" in skill
    assert "skill_name" in skill
    assert "path" in skill

    # Verify specific skill exists (e.g., langgraph-project-init)
    found = any(s["skill_name"] == "langgraph-project-init" for s in skills)
    assert found, "langgraph-project-init skill should be discovered"


def test_get_skill():
    """Test the get_skill resource function."""
    # Test retrieving a valid skill
    content = get_skill("langgraph", "langgraph-project-init")
    assert "name: langgraph-project-init" in content
    assert "# LangGraph Python Project Initialization & CI Setup" in content

    # Test error handling for non-existent skill
    with pytest.raises(ValueError, match="Skill not found"):
        get_skill("invalid-category", "invalid-skill")
