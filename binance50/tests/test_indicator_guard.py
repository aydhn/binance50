import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    IndicatorBackendError,
    LookaheadBiasError,
    UnsafeConfigurationError,
)
from binance50.safety.indicator_guard import (
    assert_backend_allowed,
    assert_indicator_config_safe,
    assert_indicator_input_safe,
    assert_indicator_output_safe,
    build_indicator_safety_report,
)


def test_config_safe():
    config = AppConfig()
    assert_indicator_config_safe(config)

    config.indicators.fill_policy = "bfill"
    with pytest.raises(UnsafeConfigurationError):
        assert_indicator_config_safe(config)

    config = AppConfig()
    config.indicators.max_columns_allowed = 6000
    with pytest.raises(UnsafeConfigurationError):
        assert_indicator_config_safe(config)


def test_input_safe():
    config = AppConfig()
    df = pd.DataFrame({"close": [1, 2], "future_return": [0.1, 0.2]})
    with pytest.raises(LookaheadBiasError):
        assert_indicator_input_safe(df, config)


def test_output_safe():
    config = AppConfig()
    config.indicators.max_columns_allowed = 2
    df = pd.DataFrame({"col1": [1], "col2": [2], "col3": [3]})
    with pytest.raises(UnsafeConfigurationError):
        assert_indicator_output_safe(df, config)


def test_backend_allowed():
    config = AppConfig()
    assert_backend_allowed("native", config)
    with pytest.raises(IndicatorBackendError):
        assert_backend_allowed("unsupported", config)


def test_safety_report():
    config = AppConfig()
    rep = build_indicator_safety_report(config)
    assert rep["status"] == "safe"
    assert rep["lookahead_prevention_active"] is True
