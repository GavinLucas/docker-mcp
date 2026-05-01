from unittest.mock import MagicMock, patch

from tools.plugins import (
    configure_plugin,
    disable_plugin,
    enable_plugin,
    get_plugin,
    install_plugin,
    list_plugins,
    push_plugin,
    remove_plugin,
    upgrade_plugin,
)


def _patch():
    return patch("tools.plugins._get_client")


def test_get_plugin():
    plugin = MagicMock()
    plugin.attrs = {"Id": "p1"}
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert get_plugin("myplugin") == {"Id": "p1"}


def test_install_plugin():
    plugin = MagicMock()
    plugin.attrs = {"Id": "p1"}
    with _patch() as mock_client:
        mock_client.return_value.plugins.install.return_value = plugin
        result = install_plugin("vieux/sshfs", local_name="sshfs")
    assert result == {"Id": "p1"}
    mock_client.return_value.plugins.install.assert_called_once_with("vieux/sshfs", local_name="sshfs")


def test_list_plugins():
    plugin = MagicMock()
    plugin.attrs = {"Id": "p1"}
    with _patch() as mock_client:
        mock_client.return_value.plugins.list.return_value = [plugin]
        assert list_plugins() == [{"Id": "p1"}]


def test_configure_plugin():
    plugin = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert configure_plugin("myplugin", {"DEBUG": "1"}) is True
    plugin.configure.assert_called_once_with({"DEBUG": "1"})


def test_disable_plugin():
    plugin = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert disable_plugin("myplugin", force=True) is True
    plugin.disable.assert_called_once_with(force=True)


def test_enable_plugin():
    plugin = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert enable_plugin("myplugin", timeout=30) is True
    plugin.enable.assert_called_once_with(timeout=30)


def test_push_plugin():
    plugin = MagicMock()
    plugin.push.return_value = {"status": "ok"}
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert push_plugin("myplugin") == {"status": "ok"}


def test_remove_plugin():
    plugin = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert remove_plugin("myplugin", force=True) is True
    plugin.remove.assert_called_once_with(force=True)


def test_upgrade_plugin_default_remote():
    plugin = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert upgrade_plugin("myplugin") is True
    plugin.upgrade.assert_called_once_with()


def test_upgrade_plugin_with_remote():
    plugin = MagicMock()
    with _patch() as mock_client:
        mock_client.return_value.plugins.get.return_value = plugin
        assert upgrade_plugin("myplugin", remote="vieux/sshfs:v2") is True
    plugin.upgrade.assert_called_once_with("vieux/sshfs:v2")
