"""FastMCP server for exposing agent skills."""

from fastmcp import FastMCP

mcp = FastMCP("agent-skills")


@mcp.tool()
def hello_skills(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: Name to greet.
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()
