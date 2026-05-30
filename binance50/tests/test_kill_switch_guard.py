import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionKillSwitchError
from binance50.safety.kill_switch_guard import assert_kill_switch_enabled

def test_kill_switch_enabled():
    config = get_config()
    assert_kill_switch_enabled(config)

    config.execution.kill_switch.enabled = False
    with pytest.raises(ExecutionKillSwitchError):
        assert_kill_switch_enabled(config)
