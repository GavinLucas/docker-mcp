import re
import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _version_tuple(version: str, length: int = 4) -> tuple[int, ...]:
    parts = [int(p) for p in version.split(".")]
    parts += [0] * (length - len(parts))
    return tuple(parts[:length])


def _dependency_name(requirement: str) -> str:
    match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", requirement)
    assert match, f"could not parse a dependency name from {requirement!r}"
    return match.group(0)


def test_intel_macos_cryptography_pin_not_relaxed():
    """
    Dependabot doesn't get an automatic Copilot review (bots aren't billable for
    premium requests), so a bump here must be caught by a hard, deterministic
    CI failure instead of relying on review. See the pyproject.toml comment:
    cryptography>=49 dropped the macosx_10_9_universal2 wheel, breaking `uvx`
    installs on Intel macOS.
    """
    data = tomllib.loads(PYPROJECT.read_text())
    deps = data["project"]["dependencies"]

    cryptography_deps = [d for d in deps if _dependency_name(d) == "cryptography"]
    assert cryptography_deps, "no direct 'cryptography' dependency found in pyproject.toml"

    intel_macos_deps = [
        d
        for d in cryptography_deps
        if "platform_system == 'Darwin'" in d and "platform_machine == 'x86_64'" in d
    ]
    assert intel_macos_deps, (
        "the Intel-macOS cryptography pin is missing: no 'cryptography' dependency is scoped to "
        f"platform_system == 'Darwin' and platform_machine == 'x86_64'; found: {cryptography_deps!r}"
    )
    assert len(intel_macos_deps) == 1, f"expected exactly one Intel-macOS cryptography pin, found: {intel_macos_deps!r}"

    dep = intel_macos_deps[0]
    m = re.search(r"cryptography\s*<\s*([0-9]+(?:\.[0-9]+)*)", dep)
    assert m, f"cryptography pin must use a '<N[.N...]' upper bound, got: {dep!r}"

    bound = _version_tuple(m.group(1))
    max_allowed = _version_tuple("49")
    assert bound <= max_allowed, (
        f"cryptography upper bound raised to {m.group(1)} — 49.x has no x86_64 macOS wheel; "
        "see the pyproject.toml comment before lifting this cap"
    )
