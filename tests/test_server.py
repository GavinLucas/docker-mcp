import subprocess
import sys

import docker_mcp  # noqa: F401 — imported for its side effect of registering every tool
from docker_mcp.server import (
    TOOL_CATEGORIES,
    ToolCategory,
    _annotations_for,
    _is_truthy,
    _seen_tool_names,
    _should_register,
    mcp,
)


def _registered_tools() -> dict:
    return mcp._tool_manager._tools


# ---------- classification stays in sync with the registered tools ----------


def test_every_registered_tool_is_classified():
    # Decorating a tool records its name in _seen_tool_names regardless of registration, so this
    # catches both a new tool missing from TOOL_CATEGORIES and a stale entry for a removed tool.
    assert _seen_tool_names == set(TOOL_CATEGORIES)


def test_all_classified_tools_are_registered_by_default():
    # With no env switches set (the test environment), every classified tool is actually registered.
    assert set(_registered_tools()) == set(TOOL_CATEGORIES)


# ---------- annotations ----------


def test_registered_tools_carry_annotations_matching_their_category():
    for name, registered in _registered_tools().items():
        ann = registered.annotations
        assert ann is not None, f"{name} has no ToolAnnotations"
        category = TOOL_CATEGORIES[name]
        assert ann.readOnlyHint is (category is ToolCategory.READ_ONLY), name
        assert ann.destructiveHint is (category is ToolCategory.DESTRUCTIVE), name


def test_annotations_for_read_only():
    ann = _annotations_for("list_containers", ToolCategory.READ_ONLY)
    assert ann.readOnlyHint is True
    assert ann.destructiveHint is False


def test_annotations_for_mutating():
    ann = _annotations_for("run_container", ToolCategory.MUTATING)
    assert ann.readOnlyHint is False
    assert ann.destructiveHint is False


def test_annotations_for_destructive_prune_is_idempotent():
    ann = _annotations_for("prune_images", ToolCategory.DESTRUCTIVE)
    assert ann.readOnlyHint is False
    assert ann.destructiveHint is True
    assert ann.idempotentHint is True


def test_annotations_for_destructive_non_prune_not_marked_idempotent():
    ann = _annotations_for("remove_container", ToolCategory.DESTRUCTIVE)
    assert ann.destructiveHint is True
    assert ann.idempotentHint is None


# ---------- env-switch logic ----------


def test_should_register_default_registers_everything():
    for category in ToolCategory:
        assert _should_register(category, readonly=False, no_destructive=False) is True


def test_should_register_readonly_keeps_only_read_only():
    assert _should_register(ToolCategory.READ_ONLY, readonly=True, no_destructive=False) is True
    assert _should_register(ToolCategory.MUTATING, readonly=True, no_destructive=False) is False
    assert _should_register(ToolCategory.DESTRUCTIVE, readonly=True, no_destructive=False) is False


def test_should_register_no_destructive_drops_only_destructive():
    assert _should_register(ToolCategory.READ_ONLY, readonly=False, no_destructive=True) is True
    assert _should_register(ToolCategory.MUTATING, readonly=False, no_destructive=True) is True
    assert _should_register(ToolCategory.DESTRUCTIVE, readonly=False, no_destructive=True) is False


def test_should_register_readonly_wins_when_both_set():
    # READONLY is the stricter switch, so a mutating tool is dropped even though NO_DESTRUCTIVE alone
    # would keep it.
    assert _should_register(ToolCategory.MUTATING, readonly=True, no_destructive=True) is False


def test_is_truthy():
    for v in ["1", "true", "TRUE", "Yes", "on", " on "]:
        assert _is_truthy(v) is True
    for v in [None, "", "0", "false", "no", "off", "nope"]:
        assert _is_truthy(v) is False


# ---------- end-to-end registration under the env switches (separate processes) ----------


def _registered_names(env_vars: list[str]) -> set[str]:
    """Import the package in a child process with the given env assignments; return the tool names."""
    code = "import docker_mcp; from docker_mcp.server import mcp; print('\\n'.join(mcp._tool_manager._tools))"
    result = subprocess.run(  # noqa: S603 — fixed argv, sys.executable, no shell; trusted test input
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=_env_with(env_vars),
        check=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def _env_with(assignments: list[str]) -> dict:
    import os

    env = dict(os.environ)
    # Clear both switches first so the parent environment can't leak into the child.
    env.pop("DOCKER_MCP_READONLY", None)
    env.pop("DOCKER_MCP_NO_DESTRUCTIVE", None)
    for assignment in assignments:
        key, _, value = assignment.partition("=")
        env[key] = value
    return env


def _names_by_category(*categories: ToolCategory) -> set[str]:
    return {name for name, c in TOOL_CATEGORIES.items() if c in categories}


def test_readonly_env_registers_exactly_the_read_only_tools():
    # Exact set comparison, not a count: registering the right number of wrong tools must fail.
    assert _registered_names(["DOCKER_MCP_READONLY=1"]) == _names_by_category(ToolCategory.READ_ONLY)


def test_no_destructive_env_registers_exactly_the_non_destructive_tools():
    expected = _names_by_category(ToolCategory.READ_ONLY, ToolCategory.MUTATING)
    assert _registered_names(["DOCKER_MCP_NO_DESTRUCTIVE=1"]) == expected


def test_default_env_registers_all_tools():
    assert _registered_names([]) == set(TOOL_CATEGORIES)


def test_both_switches_set_readonly_wins_end_to_end():
    # The precedence rule (_should_register unit-tests it) must hold through real registration too.
    names = _registered_names(["DOCKER_MCP_READONLY=1", "DOCKER_MCP_NO_DESTRUCTIVE=1"])
    assert names == _names_by_category(ToolCategory.READ_ONLY)


def test_truthy_spelling_accepted_end_to_end():
    # The switches accept "true"/"yes"/"on" spellings, not just "1".
    assert _registered_names(["DOCKER_MCP_READONLY=true"]) == _names_by_category(ToolCategory.READ_ONLY)


# ---------- typed parameter schemas ----------


def test_run_container_restart_policy_schema_is_typed():
    # The RestartPolicy TypedDict must surface as a structured schema (enum'd Name field),
    # not an opaque dict, so the agent knows the valid keys/values without guessing.
    schema = _registered_tools()["run_container"].parameters
    assert "RestartPolicy" in schema.get("$defs", {})
    rp = schema["$defs"]["RestartPolicy"]["properties"]
    assert set(rp) == {"Name", "MaximumRetryCount"}
    assert set(rp["Name"]["enum"]) == {"no", "always", "on-failure", "unless-stopped"}
