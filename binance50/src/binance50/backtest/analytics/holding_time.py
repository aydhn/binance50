import statistics
from typing import Any

from binance50.backtest.analytics.advanced_metrics import sanitize_metric
from binance50.config.models import AppConfig


def compute_avg_holding_bars(trades: list[Any]) -> float | None:
    if not trades:
        return None
    bars = [getattr(t, "holding_bars", 0) for t in trades if hasattr(t, "holding_bars")]
    if not bars:
        return None
    return sanitize_metric(sum(bars) / len(bars))


def compute_median_holding_bars(trades: list[Any]) -> float | None:
    if not trades:
        return None
    bars = [getattr(t, "holding_bars", 0) for t in trades if hasattr(t, "holding_bars")]
    if not bars:
        return None
    return sanitize_metric(statistics.median(bars))


def get_holding_bucket(bars: int) -> str:
    if bars <= 1:
        return "1 bar"
    elif bars <= 5:
        return "2-5 bars"
    elif bars <= 20:
        return "6-20 bars"
    elif bars <= 100:
        return "21-100 bars"
    else:
        return "100+ bars"


def compute_holding_time_distribution(trades: list[Any]) -> dict[str, int]:
    distribution = {"1 bar": 0, "2-5 bars": 0, "6-20 bars": 0, "21-100 bars": 0, "100+ bars": 0}

    for t in trades:
        bars = getattr(t, "holding_bars", 0)
        bucket = get_holding_bucket(bars)
        distribution[bucket] += 1

    return distribution


def compute_pnl_by_holding_bucket(trades: list[Any]) -> dict[str, float]:
    pnl = {"1 bar": 0.0, "2-5 bars": 0.0, "6-20 bars": 0.0, "21-100 bars": 0.0, "100+ bars": 0.0}

    for t in trades:
        bars = getattr(t, "holding_bars", 0)
        bucket = get_holding_bucket(bars)
        pnl[bucket] += getattr(t, "pnl_usdt", 0.0)

    return {k: sanitize_metric(v) or 0.0 for k, v in pnl.items()}


def build_holding_time_report(trades: list[Any]) -> dict[str, Any]:
    return {
        "average_holding_bars": compute_avg_holding_bars(trades),
        "median_holding_bars": compute_median_holding_bars(trades),
        "distribution": compute_holding_time_distribution(trades),
        "pnl_by_bucket": compute_pnl_by_holding_bucket(trades),
    }


def analyze_holding_times(trades: list[Any], config: AppConfig) -> dict[str, Any]:
    if not config.backtest_reporting.trade_distribution.compute_holding_time_distribution:
        return {}
    return build_holding_time_report(trades)
