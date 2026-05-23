import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionObjectDetectedError, StrategyConfigError
from binance50.safety.strategy_guard import assert_no_execution_objects, assert_strategy_config_safe


def test_strategy_config_guard():
    config = AppConfig()
    assert_strategy_config_safe(config)  # Should pass default

    config.strategies.execution_forbidden = False
    with pytest.raises(StrategyConfigError):
        assert_strategy_config_safe(config)


def test_execution_objects_guard():
    safe_dict = {"feature": "rsi", "value": 50}
    assert_no_execution_objects(safe_dict)

    unsafe_dict = {"order_id": "123"}
    with pytest.raises(ExecutionObjectDetectedError):
        assert_no_execution_objects(unsafe_dict)
