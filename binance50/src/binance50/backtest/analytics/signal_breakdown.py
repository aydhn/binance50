from typing import Any

from binance50.backtest.analytics.advanced_metrics import safe_ratio, sanitize_metric
from binance50.config.models import AppConfig


def get_score_bucket(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score < 40:
        return "0-40"
    elif score < 50:
        return "40-50"
    elif score < 65:
        return "50-65"
    elif score < 75:
        return "65-75"
    elif score < 85:
        return "75-85"
    else:
        return "85-100"


def build_score_bucket_table(trades: list[Any], score_attr: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[Any]] = {
        "0-40": [],
        "40-50": [],
        "50-65": [],
        "65-75": [],
        "75-85": [],
        "85-100": [],
        "unknown": [],
    }

    for t in trades:
        score = getattr(t, score_attr, None)
        bucket = get_score_bucket(score)
        buckets[bucket].append(t)

    table = []
    for bucket_name, bucket_trades in buckets.items():
        if not bucket_trades:
            continue

        wins = [t for t in bucket_trades if getattr(t, "pnl_usdt", 0.0) > 0]
        losses = [t for t in bucket_trades if getattr(t, "pnl_usdt", 0.0) <= 0]
        total_pnl = sum(getattr(t, "pnl_usdt", 0.0) for t in bucket_trades)

        avg_win = sum(getattr(t, "pnl_usdt", 0.0) for t in wins) / len(wins) if wins else 0.0
        avg_loss = (
            abs(sum(getattr(t, "pnl_usdt", 0.0) for t in losses) / len(losses)) if losses else 0.0
        )

        table.append(
            {
                "bucket": bucket_name,
                "count": len(bucket_trades),
                "win_rate": sanitize_metric(len(wins) / len(bucket_trades)),
                "total_pnl": sanitize_metric(total_pnl),
                "payoff_ratio": safe_ratio(avg_win, avg_loss),
            }
        )

    return table


def analyze_performance_by_signal_score(trades: list[Any], config: AppConfig) -> dict[str, Any]:
    if not config.backtest_reporting.breakdowns.by_signal_score_tier:
        return {}
    return {"table": build_score_bucket_table(trades, "signal_score")}


def analyze_performance_by_risk_score(trades: list[Any], config: AppConfig) -> dict[str, Any]:
    if not config.backtest_reporting.breakdowns.by_risk_status:
        return {}
    return {"table": build_score_bucket_table(trades, "risk_score")}


def analyze_performance_by_strategy_plugin(trades: list[Any], config: AppConfig) -> dict[str, Any]:
    if not config.backtest_reporting.breakdowns.by_strategy_plugin:
        return {}

    buckets: dict[str, list[Any]] = {}
    for t in trades:
        plugin = getattr(t, "strategy_plugin", "unknown")
        if plugin not in buckets:
            buckets[plugin] = []
        buckets[plugin].append(t)

    table = []
    for plugin, bucket_trades in buckets.items():
        wins = [t for t in bucket_trades if getattr(t, "pnl_usdt", 0.0) > 0]
        total_pnl = sum(getattr(t, "pnl_usdt", 0.0) for t in bucket_trades)
        table.append(
            {
                "plugin": plugin,
                "count": len(bucket_trades),
                "win_rate": sanitize_metric(len(wins) / len(bucket_trades)),
                "total_pnl": sanitize_metric(total_pnl),
            }
        )
    return {"table": table}


def analyze_performance_by_direction(trades: list[Any], config: AppConfig) -> dict[str, Any]:
    if not config.backtest_reporting.breakdowns.by_direction:
        return {}

    buckets: dict[str, list[Any]] = {"LONG": [], "SHORT": []}
    for t in trades:
        direction = getattr(t, "direction", "UNKNOWN").upper()
        if direction in buckets:
            buckets[direction].append(t)

    table = []
    for direction, bucket_trades in buckets.items():
        if not bucket_trades:
            continue
        wins = [t for t in bucket_trades if getattr(t, "pnl_usdt", 0.0) > 0]
        total_pnl = sum(getattr(t, "pnl_usdt", 0.0) for t in bucket_trades)
        table.append(
            {
                "direction": direction,
                "count": len(bucket_trades),
                "win_rate": sanitize_metric(len(wins) / len(bucket_trades)),
                "total_pnl": sanitize_metric(total_pnl),
            }
        )
    return {"table": table}
