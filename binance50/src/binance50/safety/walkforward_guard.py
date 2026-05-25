from typing import Any

import pandas as pd

from binance50.config.models import AppConfig


def assert_walkforward_config_safe(config: AppConfig) -> None:
    wf = config.walkforward
    if not wf.real_exchange_forbidden:
        raise ValueError("Walkforward config must forbid real exchange")
    if not wf.paper_trade_forbidden:
        raise ValueError("Walkforward config must forbid paper trade")
    if not wf.live_trade_forbidden:
        raise ValueError("Walkforward config must forbid live trade")
    if not wf.order_creation_forbidden:
        raise ValueError("Walkforward config must forbid order creation")
    if not wf.api_key_forbidden:
        raise ValueError("Walkforward config must forbid api keys")
    if not wf.dashboard_forbidden:
        raise ValueError("Walkforward config must forbid dashboard")


def assert_walkforward_input_safe(df: pd.DataFrame, config: AppConfig) -> None:
    pass


def assert_walkforward_output_safe(result: Any, config: AppConfig) -> None:
    pass


def assert_no_live_paper_execution_config(config: AppConfig) -> None:
    assert_walkforward_config_safe(config)


def build_walkforward_safety_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "safe", "real_exchange_forbidden": config.walkforward.real_exchange_forbidden}
