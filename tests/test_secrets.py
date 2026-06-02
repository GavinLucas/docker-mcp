from unittest.mock import MagicMock, patch

from docker_mcp.tools.secrets import create_secret, get_secret, list_secrets, remove_secret


def _patch():
    return patch("docker_mcp.tools.secrets._get_client")


def test_create_secret():
    secret = MagicMock()
    secret.attrs = {"ID": "sec1"}
    with _patch() as mock_client:
        mock_client.return_value.secrets.create.return_value = secret
        result = create_secret("mysecret", b"shh", labels={"a": "b"})
    assert result == {"ID": "sec1"}
    kwargs = mock_client.return_value.secrets.create.call_args.kwargs
    assert kwargs == {"name": "mysecret", "data": b"shh", "labels": {"a": "b"}}


def test_get_secret():
    secret = MagicMock()
    secret.attrs = {"ID": "sec1"}
    with _patch() as mock_client:
        mock_client.return_value.secrets.get.return_value = secret
        assert get_secret("sec1") == {"ID": "sec1"}


def test_list_secrets():
    secret = MagicMock()
    secret.attrs = {"ID": "sec1"}
    with _patch() as mock_client:
        mock_client.return_value.secrets.list.return_value = [secret]
        assert list_secrets() == [{"ID": "sec1"}]


def test_remove_secret():
    secret = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.secrets.get.return_value = secret
        assert remove_secret("sec1") is True
    secret.remove.assert_called_once()
