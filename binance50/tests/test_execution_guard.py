import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionConfigError, OrderSubmissionForbiddenError
from binance50.safety.execution_guard import assert_execution_config_safe, assert_no_order_submission_enabled

def test_execution_config_safe():
    config = get_config()
    assert_execution_config_safe(config)

def test_order_submission_forbidden():
    config = get_config()
    config.execution.global_.allow_order_submission = True
    with pytest.raises(OrderSubmissionForbiddenError):
        assert_no_order_submission_enabled(config)
