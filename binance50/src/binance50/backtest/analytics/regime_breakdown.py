from typing import Any

import pandas as pd

from binance50.backtest.analytics.advanced_metrics import safe_ratio, sanitize_metric
from binance50.config.models import AppConfig


def assign_regime_to_trades(trades: list[Any], regimes: pd.Series) -> list[dict[str, Any]]:
    # regime is assumed to be assigned at entry timestamp
    # future regime is not used
    result = []
    for t in trades:
        entry_time = getattr(t, "entry_time", None)
        regime = "unknown"
        if entry_time is not None and entry_time in regimes.index:
            regime = str(regimes.loc[entry_time])

        result.append({"trade": t, "regime": regime})
    return result


def compute_metrics_by_regime(trades_with_regime: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[Any]] = {}

    for item in trades_with_regime:
        regime = item["regime"]
        if regime not in buckets:
            buckets[regime] = []
        buckets[regime].append(item["trade"])

    metrics = {}
    for regime, trades in buckets.items():
        wins = [t for t in trades if getattr(t, "pnl_usdt", 0.0) > 0]
        losses = [t for t in trades if getattr(t, "pnl_usdt", 0.0) <= 0]
        total_pnl = sum(getattr(t, "pnl_usdt", 0.0) for t in trades)

        avg_win = sum(getattr(t, "pnl_usdt", 0.0) for t in wins) / len(wins) if wins else 0.0
        avg_loss = (
            abs(sum(getattr(t, "pnl_usdt", 0.0) for t in losses) / len(losses)) if losses else 0.0
        )

        metrics[regime] = {
            "count": len(trades),
            "win_rate": sanitize_metric(len(wins) / len(trades)) if trades else 0.0,
            "total_pnl": sanitize_metric(total_pnl),
            "payoff_ratio": safe_ratio(avg_win, avg_loss),
        }

    return metrics


def validate_regime_breakdown(metrics: dict[str, Any], config: AppConfig) -> list[str]:
    warnings = []
    min_trades = config.backtest_reporting.breakdowns.min_trades_per_bucket_warning

    for regime, data in metrics.items():
        if data["count"] < min_trades:
            warnings.append(
                f"Regime bucket '{regime}' has low trade count: {data['count']} < {min_trades}"
            )

    return warnings


def build_regime_breakdown_table(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    table = []
    for regime, data in metrics.items():
        row = {"regime": regime}
        row.update(data)
        table.append(row)
    return table


def analyze_performance_by_regime(
    trades: list[Any], equity_curve: pd.Series, regime_classifications: pd.Series, config: AppConfig
) -> dict[str, Any]:
    if not config.backtest_reporting.breakdowns.by_regime:
        return {}

    trades_with_regime = assign_regime_to_trades(trades, regime_classifications)
    metrics = compute_metrics_by_regime(trades_with_regime)
    warnings = validate_regime_breakdown(metrics, config)

    return {
        "metrics": metrics,
        "table": build_regime_breakdown_table(metrics),
        "warnings": warnings,
    }
