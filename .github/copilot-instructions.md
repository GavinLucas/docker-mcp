# GitHub Copilot Instructions

This file provides guidance to GitHub Copilot when working with code in this repository.

## Project

`docker-mcp` is a Python MCP (Model Context Protocol) server that exposes the Docker SDK for Python as MCP tools. It requires Python >=3.14 and is managed with `uv`.

## Architecture

### Entry point
The `docker_mcp` package is the entry point. `docker_mcp/__init__.py` defines `main()` and side-effect-imports the `server` and `tools` submodules (which registers all `@mcp.tool()` decorators); `docker_mcp/__main__.py` calls `main()` so `python -m docker_mcp` works.

### Server singleton (`docker_mcp/server.py`)
`docker_mcp/server.py` instantiates `FastMCP` and exports `mcp`. **Always import `mcp` from `docker_mcp.server`**, never directly from the `mcp` package in tool files — doing so creates circular imports.

```python
from docker_mcp.server import mcp
```

### Tools package (`docker_mcp/tools/`)
Each file in `docker_mcp/tools/` maps to one section of the Docker SDK documentation and contains `@mcp.tool()` decorated functions for that resource type.

| File | Docker SDK domain |
|------|-------------------|
| `docker_mcp/tools/client.py` | `DockerClient` — connection and low-level client |
| `docker_mcp/tools/containers.py` | Container lifecycle and management |
| `docker_mcp/tools/images.py` | Image pull, build, push, inspect |
| `docker_mcp/tools/networks.py` | Network create, connect, inspect |
| `docker_mcp/tools/volumes.py` | Volume create, list, remove |
| `docker_mcp/tools/configs.py` | Swarm configs |
| `docker_mcp/tools/nodes.py` | Swarm nodes |
| `docker_mcp/tools/plugins.py` | Plugin install and management |
| `docker_mcp/tools/prompts.py` | `@mcp.prompt()` templates for common docker workflows |
| `docker_mcp/tools/resources.py` | `@mcp.resource()` endpoints exposing the Docker SDK for Python docs |
| `docker_mcp/tools/secrets.py` | Swarm secrets |
| `docker_mcp/tools/services.py` | Swarm services |
| `docker_mcp/tools/swarm.py` | Swarm init, join, leave |

`docker_mcp/tools/__init__.py` re-exports all modules so `docker_mcp/__init__.py` only needs `from docker_mcp import tools`.

### Tests (`tests/`)
Each `docker_mcp/tools/<module>.py` has a corresponding `tests/test_<module>.py`. Tests use pytest. `tests/__init__.py` is intentionally empty. `tests/integration/` holds `@pytest.mark.integration` tests that require a real Docker daemon — excluded by default, run with `uv run pytest -m integration`.

## Conventions

- New Docker functionality goes in the matching `docker_mcp/tools/<domain>.py` — do not create new tool files without a corresponding entry in `docker_mcp/tools/__init__.py` and a matching test file.
- Tool functions must be decorated with `@mcp.tool` where `mcp` is imported from `docker_mcp.server`.
- Line length limit: 120 characters.
- Do not add comments that describe what the code does — only add comments for non-obvious constraints or workarounds.

### Tool function format

All `@mcp.tool` functions must follow this exact docstring format:

```python
@mcp.tool()
def mcp_example(name: str):
    """
    Say hello to someone by name.

    args: name: str - The name to say hello to
    returns: str - The greeting
    """
    return f"Hello, {name}!"
```

- One-line summary sentence, then a blank line
- `args:` section lists each parameter as `name: type - description`
- `returns:` line documents the return type and what it contains

### MCP resources

`docker_mcp/tools/resources.py` exposes `@mcp.resource(uri, mime_type=...)` endpoints (not tools) for read-only data — currently the Docker SDK for Python documentation under the `docker-docs://` URI scheme. Use the same docstring format as tools.

### MCP prompts

`docker_mcp/tools/prompts.py` exposes `@mcp.prompt(description=...)` templates that return prompt strings to guide multi-step docker workflows (deploy, migrate, troubleshoot, prune, doc lookup). Use the same docstring format as tools.

## Docker SDK Policy

**Only use `docker` module methods that are documented in the official reference.**  
Always verify the exact method name, parameter names, and return type at https://docker-py.readthedocs.io/en/stable/ before writing or suggesting code. Do not suggest methods that sound plausible but are not in the docs.

Docker SDK docs: https://docker-py.readthedocs.io/en/stable/index.html  
Docker SDK GitHub: https://github.com/docker/docker-py
