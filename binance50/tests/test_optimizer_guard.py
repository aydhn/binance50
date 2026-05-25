import pytest

from binance50.config.models import AppConfig
from binance50.optimizer.models import ParameterSpec
from binance50.safety.optimizer_guard import assert_optimizer_config_safe, assert_search_space_safe


def test_default_config_safe():
    config = AppConfig()
    assert_optimizer_config_safe(config)


def test_real_exchange_forbidden_false_hata():
    config = AppConfig()
    config.optimizer.real_exchange_forbidden = False
    with pytest.raises(ValueError):
        assert_optimizer_config_safe(config)


def test_execution_param_in_search_space_hata():
    config = AppConfig()
    specs = [
        ParameterSpec(
            name="q", path="execution.quantity", value_type="int", values=[1], description=""
        )
    ]
    with pytest.raises(ValueError):
        assert_search_space_safe(specs, config)
