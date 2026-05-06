# library of mcp resources for viewing the docker SDK documentation

import json
import urllib.request

from server import mcp

DOCKER_DOCS_BASE_URL = "https://docker-py.readthedocs.io/en/stable"

DOCS_SECTIONS = (
    "index",
    "client",
    "containers",
    "images",
    "networks",
    "volumes",
    "configs",
    "secrets",
    "nodes",
    "services",
    "swarm",
    "plugins",
)


@mcp.resource("docker-docs://contents", mime_type="application/json")
def list_docs_sections() -> str:
    """
    List the available Docker SDK documentation sections.

    returns: str - JSON describing the base URL and the available section names
    """
    return json.dumps(
        {
            "base_url": DOCKER_DOCS_BASE_URL,
            "sections": list(DOCS_SECTIONS),
            "usage": "Read docker-docs://<section> to fetch the documentation page for that section.",
        },
        indent=2,
    )


@mcp.resource("docker-docs://{section}", mime_type="text/html")
def get_docs_section(section: str) -> str:
    """
    Fetch the Docker SDK for Python documentation page for a section.

    args: section: str - Section name (e.g. "containers", "images", "swarm")
    returns: str - The HTML content of the documentation page
    """
    if section not in DOCS_SECTIONS:
        raise ValueError(
            f"Unknown documentation section '{section}'. Read docker-docs://contents to list valid sections."
        )
    url = f"{DOCKER_DOCS_BASE_URL}/{section}.html"
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")
