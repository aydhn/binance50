import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionKillSwitchError
from binance50.execution.kill_switch import is_kill_switch_active, assert_kill_switch_blocks_gateway

def test_kill_switch_active_by_default():
    config = get_config()
    assert is_kill_switch_active(config)

def test_kill_switch_blocks_gateway():
    config = get_config()
    with pytest.raises(ExecutionKillSwitchError):
        assert_kill_switch_blocks_gateway(config)
