# integration tests — require a real Docker daemon at $DOCKER_HOST (or the default unix socket).
# run with: uv run pytest -m integration

import pytest
from docker.errors import DockerException

from tools.client import df, info, ping, version
from tools.containers import list_containers
from tools.images import list_images

pytestmark = pytest.mark.integration


def _skip_if_no_daemon():
    try:
        ping()
    except (DockerException, RuntimeError) as exc:
        pytest.skip(f"Docker daemon not reachable: {exc}")


def test_ping_real_daemon():
    _skip_if_no_daemon()
    assert ping() is True


def test_version_returns_keys():
    _skip_if_no_daemon()
    payload = version()
    assert "Version" in payload
    assert "ApiVersion" in payload


def test_info_returns_keys():
    _skip_if_no_daemon()
    payload = info()
    assert "ID" in payload
    assert "ServerVersion" in payload


def test_df_returns_layers_size():
    _skip_if_no_daemon()
    payload = df()
    assert "LayersSize" in payload


def test_list_containers_returns_list():
    _skip_if_no_daemon()
    assert isinstance(list_containers(all=True), list)


def test_list_images_returns_list():
    _skip_if_no_daemon()
    assert isinstance(list_images(), list)
