import json
from unittest.mock import MagicMock, patch

import pytest

from tools.resources import (
    DOCKER_DOCS_BASE_URL,
    DOCS_SECTIONS,
    get_docs_section,
    list_docs_sections,
)


def test_list_docs_sections_returns_json_with_base_url_and_sections():
    payload = json.loads(list_docs_sections())
    assert payload["base_url"] == DOCKER_DOCS_BASE_URL
    assert payload["sections"] == list(DOCS_SECTIONS)
    assert "usage" in payload


def test_get_docs_section_fetches_expected_url():
    response = MagicMock()
    response.read.return_value = b"<html>containers</html>"
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    with patch("tools.resources.urllib.request.urlopen", return_value=response) as mock_urlopen:
        result = get_docs_section("containers")
    assert result == "<html>containers</html>"
    mock_urlopen.assert_called_once_with(f"{DOCKER_DOCS_BASE_URL}/containers.html")


def test_get_docs_section_rejects_unknown_section():
    with pytest.raises(ValueError, match="Unknown documentation section"):
        get_docs_section("not-a-section")
