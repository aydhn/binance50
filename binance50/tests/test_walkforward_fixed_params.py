import pytest

from binance50.config.models import AppConfig
from binance50.walkforward.fixed_params import (
    build_fixed_parameter_set_from_config,
    validate_fixed_parameter_set,
)


def test_fixed_params():
    config = AppConfig()
    param = {"trend": 20}
    fp = build_fixed_parameter_set_from_config(config, param)
    assert fp.hash != ""


def test_fixed_params_execution_rejected():
    config = AppConfig()
    param = {"order_id": "123"}
    with pytest.raises(ValueError):
        validate_fixed_parameter_set(param, config)
