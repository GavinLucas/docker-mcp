"""MCP server for managing Docker resources and searching Docker documentation"""

from docker_mcp.server import mcp
from docker_mcp import tools  # noqa: F401  -- imported for side effects (registers @mcp.tool() decorators)


def main():
    """
    Main function to run the MCP server.
    """
    mcp.run(transport="stdio")
