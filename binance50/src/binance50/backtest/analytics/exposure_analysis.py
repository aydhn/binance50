from typing import Any

import pandas as pd

from binance50.backtest.analytics.advanced_metrics import sanitize_metric
from binance50.config.models import AppConfig


def compute_time_in_market(equity_curve: pd.Series) -> float | None:
    if len(equity_curve) < 2:
        return None
    # For now, just placeholder
    return None


def compute_average_open_positions(equity_curve: pd.Series) -> float | None:
    # Requires positional data overlay, placeholder for now
    return None


def compute_max_open_positions(equity_curve: pd.Series) -> int | None:
    return None


def compute_turnover_from_trades(trades: list[Any]) -> float | None:
    if not trades:
        return None
    # Total notional traded / starting capital
    notional = sum(
        getattr(t, "entry_price", 0.0) * getattr(t, "quantity", 0.0) * 2 for t in trades
    )  # approx entry + exit
    return sanitize_metric(notional)


def compute_notional_usage(trades: list[Any], equity_curve: pd.Series) -> float | None:
    return None


def build_exposure_report(result: Any, config: AppConfig) -> dict[str, Any]:
    trades = getattr(result, "trades", [])
    equity = getattr(result, "equity_curve", pd.Series(dtype=float))

    return {
        "time_in_market_pct": compute_time_in_market(equity),
        "average_open_positions": compute_average_open_positions(equity),
        "max_open_positions": compute_max_open_positions(equity),
        "turnover_notional": compute_turnover_from_trades(trades),
        "max_notional_usage_pct": compute_notional_usage(trades, equity),
        "metadata": {"simulation_note": "Exposure values are simulated based on backtest fills."},
    }


def analyze_exposure(result: Any, config: AppConfig) -> dict[str, Any]:
    return build_exposure_report(result, config)
