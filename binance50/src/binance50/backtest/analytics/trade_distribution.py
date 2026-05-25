from typing import Any

import numpy as np

from binance50.backtest.analytics.advanced_metrics import sanitize_metric
from binance50.config.models import AppConfig


def compute_win_loss_distribution(trades: list[Any]) -> dict[str, Any]:
    if not trades:
        return {}

    wins = [t for t in trades if getattr(t, "pnl_usdt", 0.0) > 0]
    losses = [t for t in trades if getattr(t, "pnl_usdt", 0.0) <= 0]

    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": sanitize_metric(len(wins) / len(trades)),
        "loss_rate": sanitize_metric(len(losses) / len(trades)),
    }


def compute_trade_return_histogram(trades: list[Any], bins: int) -> dict[str, Any]:
    if not trades:
        return {}

    returns = [getattr(t, "return_pct", 0.0) for t in trades]
    if not returns:
        return {}

    hist, edges = np.histogram(returns, bins=bins)

    return {"counts": [int(x) for x in hist], "edges": [sanitize_metric(x) for x in edges]}


def compute_best_worst_trades(trades: list[Any], top_n: int) -> dict[str, Any]:
    if not trades:
        return {"best": [], "worst": []}

    # Sort by pnl_usdt
    sorted_trades = sorted(trades, key=lambda x: getattr(x, "pnl_usdt", 0.0))

    worst = sorted_trades[:top_n]
    best = sorted_trades[-top_n:]
    best.reverse()  # Largest positive first

    return {
        "best": [
            {"id": getattr(t, "id", ""), "pnl": sanitize_metric(getattr(t, "pnl_usdt", 0.0))}
            for t in best
        ],
        "worst": [
            {"id": getattr(t, "id", ""), "pnl": sanitize_metric(getattr(t, "pnl_usdt", 0.0))}
            for t in worst
        ],
    }


def compute_consecutive_wins_losses(trades: list[Any]) -> dict[str, Any]:
    if not trades:
        return {"max_consecutive_wins": 0, "max_consecutive_losses": 0}

    max_wins = 0
    max_losses = 0
    current_wins = 0
    current_losses = 0

    for t in trades:
        pnl = getattr(t, "pnl_usdt", 0.0)
        if pnl > 0:
            current_wins += 1
            current_losses = 0
            max_wins = max(max_wins, current_wins)
        else:
            current_losses += 1
            current_wins = 0
            max_losses = max(max_losses, current_losses)

    return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}


def compute_trade_pnl_percentiles(trades: list[Any]) -> dict[str, Any]:
    if not trades:
        return {}

    pnls = [getattr(t, "pnl_usdt", 0.0) for t in trades]
    if not pnls:
        return {}

    percentiles = [5, 25, 50, 75, 95]
    values = np.percentile(pnls, percentiles)

    return {f"p{p}": sanitize_metric(v) for p, v in zip(percentiles, values, strict=False)}


def compute_trade_return_percentiles(trades: list[Any]) -> dict[str, Any]:
    if not trades:
        return {}

    returns = [getattr(t, "return_pct", 0.0) for t in trades]
    if not returns:
        return {}

    percentiles = [5, 25, 50, 75, 95]
    values = np.percentile(returns, percentiles)

    return {f"p{p}": sanitize_metric(v) for p, v in zip(percentiles, values, strict=False)}


def validate_trade_distribution(report: dict[str, Any]) -> None:
    pass


def analyze_trade_distribution(trades: list[Any], config: AppConfig) -> dict[str, Any]:
    return {}
