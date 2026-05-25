from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindowResult
from binance50.walkforward.parameter_drift import ParameterDriftReport


class WalkForwardStabilityReport(BaseModel):
    run_id: str
    window_count: int
    completed_window_count: int
    oos_positive_window_ratio: float
    oos_return_mean: float
    oos_return_std: float
    oos_drawdown_mean: float
    oos_drawdown_std: float
    oos_trade_count_mean: float
    oos_trade_count_std: float
    score_stability: float
    return_stability: float
    drawdown_stability: float
    trade_count_stability: float
    parameter_stability: float
    final_stability_score: float
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def compute_walkforward_stability(
    window_results: dict[str, WalkForwardWindowResult],
    parameter_drift_reports: list[ParameterDriftReport],
    config: AppConfig,
) -> WalkForwardStabilityReport:
    completed = [r for r in window_results.values() if r.status == "completed"]
    window_count = len(window_results)
    completed_count = len(completed)

    if completed_count == 0:
        return WalkForwardStabilityReport(
            run_id="unknown",
            window_count=window_count,
            completed_window_count=0,
            oos_positive_window_ratio=0.0,
            oos_return_mean=0.0,
            oos_return_std=0.0,
            oos_drawdown_mean=0.0,
            oos_drawdown_std=0.0,
            oos_trade_count_mean=0.0,
            oos_trade_count_std=0.0,
            score_stability=0.0,
            return_stability=0.0,
            drawdown_stability=0.0,
            trade_count_stability=0.0,
            parameter_stability=0.0,
            final_stability_score=0.0,
        )

    oos_returns = [
        r.oos_report.get("metrics", {}).get("cagr", 0.0) for r in completed if r.oos_report
    ]
    oos_drawdowns = [
        r.oos_report.get("metrics", {}).get("max_drawdown", 0.0) for r in completed if r.oos_report
    ]
    oos_trades = [
        r.oos_report.get("metrics", {}).get("trade_count", 0) for r in completed if r.oos_report
    ]

    return_mean = np.mean(oos_returns) if oos_returns else 0.0
    return_std = np.std(oos_returns) if len(oos_returns) > 1 else 0.0

    drawdown_mean = np.mean(oos_drawdowns) if oos_drawdowns else 0.0
    drawdown_std = np.std(oos_drawdowns) if len(oos_drawdowns) > 1 else 0.0

    trade_mean = np.mean(oos_trades) if oos_trades else 0.0
    trade_std = np.std(oos_trades) if len(oos_trades) > 1 else 0.0

    positive_ratio = compute_positive_oos_window_ratio(window_results)

    ret_stability = compute_metric_stability(oos_returns)
    dd_stability = compute_metric_stability([-x for x in oos_drawdowns])  # Invert drawdown
    trade_stability = compute_metric_stability(oos_trades)
    param_stability = compute_parameter_stability_from_drift(parameter_drift_reports)

    # Calculate simple final score
    final_score = (ret_stability + dd_stability + trade_stability + param_stability) / 4.0
    final_score = max(min(final_score, 100.0), 0.0)

    warnings = []
    if completed_count < config.walkforward.mode.min_windows_required:
        warnings.append("Insufficient completed windows for reliable stability score")

    if (
        final_score < config.walkforward.stability.min_stability_score
        and config.walkforward.stability.warn_unstable_windows
    ):
        warnings.append(
            f"Walk-forward stability score ({final_score:.2f}) is below minimum threshold"
        )

    return WalkForwardStabilityReport(
        run_id="unknown",
        window_count=window_count,
        completed_window_count=completed_count,
        oos_positive_window_ratio=positive_ratio,
        oos_return_mean=float(return_mean),
        oos_return_std=float(return_std),
        oos_drawdown_mean=float(drawdown_mean),
        oos_drawdown_std=float(drawdown_std),
        oos_trade_count_mean=float(trade_mean),
        oos_trade_count_std=float(trade_std),
        score_stability=ret_stability,  # proxy
        return_stability=ret_stability,
        drawdown_stability=dd_stability,
        trade_count_stability=trade_stability,
        parameter_stability=param_stability,
        final_stability_score=final_score,
        warnings=warnings,
    )


def compute_positive_oos_window_ratio(window_results: dict[str, WalkForwardWindowResult]) -> float:
    completed = [r for r in window_results.values() if r.status == "completed"]
    if not completed:
        return 0.0
    positive_count = sum(
        1 for r in completed if r.oos_report and r.oos_report.get("metrics", {}).get("cagr", 0) > 0
    )
    return positive_count / len(completed)


def compute_metric_stability(values: list[float]) -> float:
    if len(values) < 2:
        return 50.0  # Neutral
    mean = np.mean(values)
    std = np.std(values)

    if std == 0:
        return 100.0 if mean > 0 else 50.0

    cv = abs(std / mean) if mean != 0 else float("inf")

    # Map CV to 0-100 score
    score = max(100.0 - (cv * 50), 0.0)
    return score


def compute_parameter_stability_from_drift(drift_reports: list[ParameterDriftReport]) -> float:
    if not drift_reports:
        return 100.0

    avg_drift = sum(r.total_drift_score for r in drift_reports) / len(drift_reports)
    # Map 0 drift to 100 score, 1 drift to 0 score
    score = max(100.0 - (avg_drift * 100), 0.0)
    return score


def classify_walkforward_stability(report: WalkForwardStabilityReport, config: AppConfig) -> str:
    if report.final_stability_score >= 80:
        return "highly_stable"
    elif report.final_stability_score >= 50:
        return "stable"
    elif report.final_stability_score >= 25:
        return "unstable"
    else:
        return "highly_unstable"
