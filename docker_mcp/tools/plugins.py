# library of mcp tools relating to plugin management

from docker_mcp.server import tool
from docker_mcp.tools.client import _get_client


@tool()
def get_plugin(name: str, host: str | None = None) -> dict:
    """
    Get an installed plugin by name.

    args: name - The plugin name
    returns: dict - The plugin's attrs
    """
    return _get_client(host).plugins.get(name).attrs


@tool()
def install_plugin(remote_name: str, local_name: str | None = None, host: str | None = None) -> dict:
    """
    Install a plugin from a remote reference.

    args:
        remote_name - The remote plugin reference
        local_name - Optional local name for the plugin
    returns: dict - The installed plugin's attrs
    """
    return _get_client(host).plugins.install(remote_name, local_name=local_name).attrs


@tool()
def list_plugins(host: str | None = None) -> list:
    """
    List installed plugins.

    returns: list - A list of plugin attrs dicts
    """
    return [p.attrs for p in _get_client(host).plugins.list()]


@tool()
def configure_plugin(name: str, options: dict, host: str | None = None) -> bool:
    """
    Set runtime configuration options on an installed plugin.

    Use `get_plugin` first to see which keys the plugin exposes under `Settings.Env`; pass
    those same keys as a plain dict, e.g. `{"DEBUG": "1", "SOCKET": "/run/x.sock"}`. The
    plugin must be disabled before reconfiguring — call `disable_plugin` first if it is
    currently active, then `enable_plugin` afterwards to apply the new settings.

    args:
        name - Plugin name or id (e.g. "vieux/sshfs:latest")
        options - Key/value settings to apply, matching the plugin's declared env keys
    returns: bool - True after configuration
    """
    _get_client(host).plugins.get(name).configure(options)
    return True


@tool()
def disable_plugin(name: str, force: bool = False, host: str | None = None) -> bool:
    """
    Disable a plugin so it stops intercepting Docker API calls; the plugin remains installed.

    A disabled plugin cannot be used by new containers but existing containers that already
    have it attached are unaffected. Use `force=True` to disable even if active containers
    are still using it — this may cause those containers to lose access to plugin-provided
    resources (e.g. a volume driver). Re-enable with `enable_plugin`.

    args:
        name - Plugin name or id
        force - Disable even if active containers are using the plugin (may disrupt them)
    returns: bool - True after the plugin is disabled
    """
    _get_client(host).plugins.get(name).disable(force=force)
    return True


@tool()
def enable_plugin(name: str, timeout: int = 0, host: str | None = None) -> bool:
    """
    Enable a plugin.

    args:
        name - The plugin name
        timeout - Timeout in seconds (0 means no timeout)
    returns: bool - True after the plugin is enabled
    """
    _get_client(host).plugins.get(name).enable(timeout=timeout)
    return True


@tool()
def push_plugin(name: str, host: str | None = None) -> dict:
    """
    Push a locally built or pulled plugin image to a remote registry.

    The daemon must already be authenticated with the target registry — call `login` first if
    needed. `name` must include the registry host for any registry other than Docker Hub,
    e.g. "registry.example.com/myplugin:1.0". The plugin must exist locally (use
    `install_plugin` or `build` to create it first).

    args: name - Plugin name including tag, e.g. "myorg/myplugin:latest"
    returns: dict - Push progress/status events returned by the daemon
    """
    return _get_client(host).plugins.get(name).push()


@tool()
def remove_plugin(name: str, force: bool = False, host: str | None = None) -> bool:
    """
    Remove a plugin.

    args:
        name - The plugin name
        force - Force removal even if the plugin is enabled
    returns: bool - True after removal
    """
    _get_client(host).plugins.get(name).remove(force=force)
    return True


@tool()
def upgrade_plugin(name: str, remote: str | None = None, host: str | None = None) -> bool:
    """
    Upgrade a plugin.

    args:
        name - The plugin name
        remote - Remote reference to upgrade from (defaults to current name)
    returns: bool - True after the upgrade completes
    """
    plugin = _get_client(host).plugins.get(name)
    if remote is None:
        plugin.upgrade()
    else:
        plugin.upgrade(remote)
    return True
