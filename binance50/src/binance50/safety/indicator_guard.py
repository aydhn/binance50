from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    IndicatorBackendError,
    UnsafeConfigurationError,
)
from binance50.indicators.validators import assert_no_lookahead_columns


def assert_indicator_config_safe(config: AppConfig) -> None:
    if config.indicators.fill_policy == "bfill":
        raise UnsafeConfigurationError("fill_policy 'bfill' carries extreme lookahead bias risk and is forbidden in Phase 11")

    if config.indicators.max_columns_allowed > 5000:
        raise UnsafeConfigurationError("max_columns_allowed exceeds hard safety limit of 5000")

def assert_indicator_input_safe(df: pd.DataFrame, config: AppConfig) -> None:
    assert_no_lookahead_bias_columns(df)

def assert_no_lookahead_bias_columns(df: pd.DataFrame) -> None:
    assert_no_lookahead_columns(df)

def assert_indicator_output_safe(df: pd.DataFrame, config: AppConfig) -> None:
    assert_no_lookahead_columns(df)

    if len(df.columns) > config.indicators.max_columns_allowed:
        raise UnsafeConfigurationError(f"Output columns ({len(df.columns)}) exceeds allowed ({config.indicators.max_columns_allowed})")

def assert_backend_allowed(backend: str, config: AppConfig) -> None:
    if backend not in config.indicators.allowed_backends:
        raise IndicatorBackendError(f"Backend '{backend}' is not in allowed_backends")

def build_indicator_safety_report(config: AppConfig) -> dict[str, Any]:
    try:
        assert_indicator_config_safe(config)
        status = "safe"
        reasons = []
    except UnsafeConfigurationError as e:
        status = "unsafe"
        reasons = [str(e)]

    return {
        "status": status,
        "reasons": reasons,
        "lookahead_prevention_active": config.indicators.prevent_lookahead_bias,
        "fill_policy": config.indicators.fill_policy
    }
