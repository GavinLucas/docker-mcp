import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from docker_mcp.tools.resources import (
    DOCKER_DOCS_BASE_URL,
    EXTERNAL_SECTIONS,
    SDK_SECTIONS,
    get_docs_section,
    list_docs_sections,
)


def test_list_docs_sections_returns_json_with_sdk_and_external_sections():
    payload = json.loads(list_docs_sections())
    # Backward-compatible fields: `base_url` (SDK base) and `sections` (list of section names).
    assert payload["base_url"] == DOCKER_DOCS_BASE_URL
    assert payload["sdk_base_url"] == DOCKER_DOCS_BASE_URL
    assert isinstance(payload["sections"], list)
    for section in SDK_SECTIONS:
        assert section in payload["sections"]
    for section in EXTERNAL_SECTIONS:
        assert section in payload["sections"]
    # New field: `section_urls` maps each section name to its absolute URL.
    for section in SDK_SECTIONS:
        assert payload["section_urls"][section] == f"{DOCKER_DOCS_BASE_URL}/{section}.html"
    for section, url in EXTERNAL_SECTIONS.items():
        assert payload["section_urls"][section] == url
    assert "usage" in payload


def _docs_response(body: bytes) -> MagicMock:
    response = MagicMock()
    response.content = body
    response.raise_for_status.return_value = None
    return response


def test_get_docs_section_fetches_sdk_section_at_base_url():
    with patch(
        "docker_mcp.tools.resources.httpx.get", return_value=_docs_response(b"<html>containers</html>")
    ) as mock_get:
        result = get_docs_section("containers")
    assert result == "<html>containers</html>"
    args, kwargs = mock_get.call_args
    assert args[0] == f"{DOCKER_DOCS_BASE_URL}/containers.html"
    # A bounded timeout is mandatory — a stalled fetch must not hang the resource read.
    assert kwargs["timeout"] == 30.0


def test_get_docs_section_fetches_external_section_at_absolute_url():
    with patch(
        "docker_mcp.tools.resources.httpx.get", return_value=_docs_response(b"<html>compose</html>")
    ) as mock_get:
        result = get_docs_section("compose")
    assert result == "<html>compose</html>"
    assert mock_get.call_args.args[0] == EXTERNAL_SECTIONS["compose"]


def test_get_docs_section_raises_for_status():
    response = MagicMock()
    response.content = b""
    response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock())
    with patch("docker_mcp.tools.resources.httpx.get", return_value=response):
        with pytest.raises(httpx.HTTPStatusError):
            get_docs_section("containers")


def test_get_docs_section_rejects_unknown_section():
    with pytest.raises(ValueError, match="Unknown documentation section"):
        get_docs_section("not-a-section")
