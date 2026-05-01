from unittest.mock import MagicMock, patch

from tools.swarm import (
    get_swarm_unlock_key,
    init_swarm,
    join_swarm,
    leave_swarm,
    reload_swarm,
    unlock_swarm,
    update_swarm,
)


def _patch():
    return patch("tools.swarm._get_client")


def test_init_swarm():
    with _patch() as mock_client:
        mock_client.return_value.swarm.init.return_value = "node-id"
        assert init_swarm(advertise_addr="10.0.0.1") == "node-id"
    kwargs = mock_client.return_value.swarm.init.call_args.kwargs
    assert kwargs["advertise_addr"] == "10.0.0.1"
    assert kwargs["listen_addr"] == "0.0.0.0:2377"


def test_join_swarm():
    with _patch() as mock_client:
        mock_client.return_value.swarm.join.return_value = True
        assert join_swarm(["10.0.0.1:2377"], "TOKEN") is True
    kwargs = mock_client.return_value.swarm.join.call_args.kwargs
    assert kwargs["remote_addrs"] == ["10.0.0.1:2377"]
    assert kwargs["join_token"] == "TOKEN"


def test_leave_swarm():
    with _patch() as mock_client:
        mock_client.return_value.swarm.leave.return_value = True
        assert leave_swarm(force=True) is True
    mock_client.return_value.swarm.leave.assert_called_once_with(force=True)


def test_update_swarm():
    with _patch() as mock_client:
        mock_client.return_value.swarm.update.return_value = True
        assert update_swarm(rotate_worker_token=True) is True
    mock_client.return_value.swarm.update.assert_called_once_with(
        rotate_worker_token=True,
        rotate_manager_token=False,
        rotate_manager_unlock_key=False,
    )


def test_reload_swarm():
    swarm = MagicMock()
    swarm.attrs = {"ID": "swarm1"}
    with _patch() as mock_client:
        mock_client.return_value.swarm = swarm
        assert reload_swarm() == {"ID": "swarm1"}
    swarm.reload.assert_called_once()


def test_unlock_swarm():
    with _patch() as mock_client:
        mock_client.return_value.swarm.unlock.return_value = True
        assert unlock_swarm("KEY") is True
    mock_client.return_value.swarm.unlock.assert_called_once_with("KEY")


def test_get_swarm_unlock_key():
    with _patch() as mock_client:
        mock_client.return_value.swarm.get_unlock_key.return_value = {"UnlockKey": "K"}
        assert get_swarm_unlock_key() == {"UnlockKey": "K"}
