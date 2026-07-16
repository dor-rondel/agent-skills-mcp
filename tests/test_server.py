"""Tests for the FastMCP server."""

from agent_skills_server.server import hello_skills


def test_hello_skills():
    """Test the hello_skills tool function."""
    assert hello_skills("test") == "Hello, test!"
    assert hello_skills() == "Hello, World!"
