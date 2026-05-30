import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionModeError
from binance50.execution.modes import (
    assert_mode_can_create_draft,
    assert_mode_cannot_submit_order,
    assert_mode_cannot_call_gateway,
    validate_mode_enabled,
)
from binance50.execution.models import ExecutionMode

def test_sandbox_mode_policy():
    config = get_config()
    validate_mode_enabled(ExecutionMode.sandbox, config)
    assert_mode_can_create_draft(ExecutionMode.sandbox, config)
    assert_mode_cannot_submit_order(ExecutionMode.sandbox, config)
    assert_mode_cannot_call_gateway(ExecutionMode.sandbox, config)

def test_live_mode_policy_disabled_by_default():
    config = get_config()
    with pytest.raises(ExecutionModeError):
        validate_mode_enabled(ExecutionMode.live_candidate, config)
