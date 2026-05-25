from typing import Any

import pandas as pd

from binance50.backtest.analytics.advanced_metrics import sanitize_metric
from binance50.config.models import AppConfig


def compute_underwater_curve(equity_curve: pd.Series) -> pd.Series:
    if len(equity_curve) < 2:
        return pd.Series(dtype=float)
    running_max = equity_curve.cummax()
    underwater = (equity_curve - running_max) / running_max
    return underwater


def detect_top_drawdowns(equity_curve: pd.Series, top_n: int) -> list[dict[str, Any]]:
    underwater = compute_underwater_curve(equity_curve)
    if underwater.empty:
        return []

    drawdowns = []
    in_drawdown = False
    peak_idx = None
    trough_idx = None
    max_dd = 0.0

    for idx, val in underwater.items():
        if val < 0:
            if not in_drawdown:
                in_drawdown = True
                peak_idx = idx

            if val < max_dd:
                max_dd = float(val)
                trough_idx = idx
        elif val == 0 and in_drawdown:
            in_drawdown = False
            drawdowns.append(
                {
                    "start": peak_idx.isoformat() if peak_idx else None,
                    "trough": trough_idx.isoformat() if trough_idx else None,
                    "end": idx.isoformat() if idx else None,
                    "depth": sanitize_metric(max_dd),
                    "recovered": True,
                }
            )
            max_dd = 0.0

    # Handle unrecovered drawdown
    if in_drawdown:
        drawdowns.append(
            {
                "start": peak_idx.isoformat() if peak_idx else None,
                "trough": trough_idx.isoformat() if trough_idx else None,
                "end": None,
                "depth": sanitize_metric(max_dd),
                "recovered": False,
            }
        )

    # Sort by depth and take top N
    drawdowns.sort(key=lambda x: x["depth"] if x["depth"] is not None else 0.0)
    return drawdowns[:top_n]


def compute_drawdown_duration(drawdown_series: pd.Series) -> dict[str, Any]:
    # Placeholder for computing duration statistics from the underwater curve
    return {}


def compute_recovery_time(drawdown_event: dict[str, Any]) -> int | None:
    if not drawdown_event.get("recovered", False):
        return None

    # A real implementation would parse datetime strings and return periods
    return None


def compute_average_drawdown(drawdown_events: list[dict[str, Any]]) -> float | None:
    if not drawdown_events:
        return None

    depths = [d["depth"] for d in drawdown_events if d["depth"] is not None]
    if not depths:
        return None

    return sanitize_metric(sum(depths) / len(depths))


def build_drawdown_v2_report(result: Any, config: AppConfig) -> dict[str, Any]:
    return {}
