# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`docker-mcp` is a Python MCP server (requires Python >=3.14) managed with `uv` that exposes the Docker SDK for Python as MCP tools. The entry point is `main.py`.

## Commands

```bash
# Install dependencies
uv sync

# Run the project
uv run python main.py

# Add a dependency
uv add <package>

# Run unit tests (integration tests are excluded by default)
uv run pytest -v

# Run integration tests (require a real Docker daemon)
uv run pytest -m integration -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Type-check
uv run pyright

# Install pre-commit hooks (one-time)
uv run pre-commit install
```

## Architecture

### Entry point
`main.py` imports `server` and `tools`, then calls `mcp.run(transport="stdio")`.

### Server singleton (`server.py`)
Instantiates `FastMCP` and exports the `mcp` object. **All tool modules import `mcp` from here** — never import from `mcp` directly in tool files, as this would create circular imports.

```python
from server import mcp
```

### Tools package (`tools/`)
Each file maps to one section of the Docker SDK documentation and contains `@mcp.tool()` decorated functions for that resource type. `tools/__init__.py` imports all modules with `*` so `main.py` only needs `import tools`.

| File | Docker SDK domain |
|------|-------------------|
| `tools/client.py` | `DockerClient` — connection and low-level client |
| `tools/containers.py` | Container lifecycle and management |
| `tools/images.py` | Image pull, build, push, inspect |
| `tools/networks.py` | Network create, connect, inspect |
| `tools/volumes.py` | Volume create, list, remove |
| `tools/configs.py` | Swarm configs |
| `tools/nodes.py` | Swarm nodes |
| `tools/plugins.py` | Plugin install and management |
| `tools/prompts.py` | `@mcp.prompt()` templates for common docker workflows |
| `tools/resources.py` | `@mcp.resource()` endpoints exposing the Docker SDK for Python docs |
| `tools/secrets.py` | Swarm secrets |
| `tools/services.py` | Swarm services |
| `tools/swarm.py` | Swarm init, join, leave |

### Tests (`tests/`)
Each `tools/<module>.py` has a corresponding `tests/test_<module>.py`. Tests use pytest. The `tests/__init__.py` is intentionally empty.

`tests/integration/` holds tests that hit a real Docker daemon. They are marked `@pytest.mark.integration` (or `pytestmark = pytest.mark.integration` at module level) and excluded by default via `addopts = "-m 'not integration'"` in `pyproject.toml`. Each test calls `_skip_if_no_daemon()` so the suite skips cleanly when no daemon is reachable.

## Conventions

- New Docker functionality goes in the matching `tools/<domain>.py` file, not in a new file.
- Every new `tools/` file must be imported in `tools/__init__.py`.
- Every new `tools/<module>.py` must have a matching `tests/test_<module>.py`.
- Tool functions are decorated with `@mcp.tool` and imported from `server.py`.
- Line length limit: 120 characters (enforced by ruff and flake8).

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

`tools/resources.py` exposes `@mcp.resource(uri, mime_type=...)` endpoints (not tools) for read-only data — currently the Docker SDK for Python documentation under the `docker-docs://` URI scheme. Resources follow the same docstring format as tools and are also star-imported via `tools/__init__.py`.

### MCP prompts

`tools/prompts.py` exposes `@mcp.prompt(description=...)` templates that return rendered prompt strings to guide multi-step docker workflows (deploy, migrate, troubleshoot, prune, doc lookup). Prompts follow the same docstring format as tools and are star-imported via `tools/__init__.py`.

## Docker SDK Policy

**Before writing or modifying any code that calls the Docker SDK (`docker` package), you MUST run `/docker-sdk` (or `/docker-sdk <topic>`) to:**
1. Verify exact method signatures from the live Docker SDK for Python documentation
2. Confirm parameter names and return types before writing code
3. Never use a `docker` module method that has not been confirmed in the docs

Do not assume any method exists because it sounds plausible. If you cannot confirm it from the documentation, say so and do not use it.

Docker SDK docs: https://docker-py.readthedocs.io/en/stable/index.html  
Docker SDK GitHub: https://github.com/docker/docker-py
