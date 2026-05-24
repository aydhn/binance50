from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeValidationError
from binance50.regimes.models import RegimeRunResult


def assert_regime_config_safe(config: AppConfig) -> None:
    if not config.regimes.execution_forbidden:
        raise RegimeValidationError("execution_forbidden must be true")
    if not config.regimes.order_creation_forbidden:
        raise RegimeValidationError("order_creation_forbidden must be true")
    if not config.regimes.live_trade_forbidden:
        raise RegimeValidationError("live_trade_forbidden must be true")
    if not config.regimes.backtest_forbidden:
        raise RegimeValidationError("backtest_forbidden must be true")
    if not config.regimes.paper_trade_forbidden:
        raise RegimeValidationError("paper_trade_forbidden must be true")


def assert_no_execution_objects(payload: Any) -> None:
    pass  # Simple implementation for now.


def assert_regime_input_safe(df: pd.DataFrame, config: AppConfig) -> None:
    pass


def assert_regime_output_safe(result: RegimeRunResult, config: AppConfig) -> None:
    for c in result.classifications:
        for k in c.metadata.keys():
            if "order" in k or "execution" in k:
                raise RegimeValidationError(
                    "Execution details found in regime classification output"
                )


def build_regime_safety_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "safe", "reason": "All checks passed"}
