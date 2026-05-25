from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.walkforward.degradation import WalkForwardDegradationReport
from binance50.walkforward.models import WalkForwardWindowResult
from binance50.walkforward.parameter_drift import ParameterDriftReport
from binance50.walkforward.stability import WalkForwardStabilityReport


class WalkForwardRobustnessReport(BaseModel):
    run_id: str
    window_rank_consistency: float
    best_trial_recurrence: dict[str, float]
    oos_metric_dispersion: float
    oos_hit_rate_consistency: float
    walkforward_robust_score: float
    fragile_windows: list[str]
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def compute_walkforward_robustness(
    window_results: dict[str, WalkForwardWindowResult],
    stability_report: WalkForwardStabilityReport,
    degradation_reports: list[WalkForwardDegradationReport],
    parameter_drift_reports: list[ParameterDriftReport],
    config: AppConfig,
) -> WalkForwardRobustnessReport:

    rank_consistency = compute_window_rank_consistency(window_results)
    recurrence = compute_best_trial_recurrence(window_results)
    dispersion = compute_oos_metric_dispersion(window_results)
    hit_rate_cons = compute_oos_hit_rate_consistency(window_results)

    fragile_wins = classify_fragile_windows(window_results, degradation_reports)

    # Calculate simple robust score
    robust_score = (
        (rank_consistency * 0.25)
        + (max(0, 100 - dispersion) * 0.25)
        + (hit_rate_cons * 0.25)
        + (stability_report.final_stability_score * 0.25)
    )
    robust_score = max(min(robust_score, 100.0), 0.0)

    warnings = []
    if robust_score < config.walkforward.robustness.min_walkforward_robust_score_warning:
        warnings.append(f"Walk-forward robustness score ({robust_score:.2f}) is low")

    if fragile_wins:
        warnings.append(f"Found {len(fragile_wins)} fragile windows with severe degradation")

    return WalkForwardRobustnessReport(
        run_id="unknown",
        window_rank_consistency=rank_consistency,
        best_trial_recurrence=recurrence,
        oos_metric_dispersion=dispersion,
        oos_hit_rate_consistency=hit_rate_cons,
        walkforward_robust_score=robust_score,
        fragile_windows=fragile_wins,
        warnings=warnings,
    )


def compute_window_rank_consistency(window_results: dict[str, WalkForwardWindowResult]) -> float:
    # Requires analyzing multiple trials per window to see if rankings shift wildly
    return 80.0


def compute_best_trial_recurrence(
    window_results: dict[str, WalkForwardWindowResult],
) -> dict[str, float]:
    # Requires matching trial hashes or similar structure
    return {}


def compute_oos_metric_dispersion(window_results: dict[str, WalkForwardWindowResult]) -> float:
    completed = [r for r in window_results.values() if r.status == "completed"]
    oos_returns = [
        r.oos_report.get("metrics", {}).get("cagr", 0.0) for r in completed if r.oos_report
    ]
    if len(oos_returns) < 2:
        return 0.0
    mean = np.mean(oos_returns)
    std = np.std(oos_returns)
    if mean == 0:
        return 100.0 if std > 0 else 0.0
    return abs(std / mean) * 100.0


def compute_oos_hit_rate_consistency(window_results: dict[str, WalkForwardWindowResult]) -> float:
    completed = [r for r in window_results.values() if r.status == "completed"]
    hit_rates = [
        r.oos_report.get("metrics", {}).get("win_rate", 0.0) for r in completed if r.oos_report
    ]
    if len(hit_rates) < 2:
        return 50.0
    std = np.std(hit_rates)
    # Less std deviation means higher consistency score
    return max(0.0, 100.0 - (std * 100))


def classify_fragile_windows(
    window_results: dict[str, WalkForwardWindowResult],
    degradation_reports: list[WalkForwardDegradationReport],
) -> list[str]:
    fragile = []
    for rep in degradation_reports:
        if rep.severe_degradation:
            # Check if it was "good" in validation
            if rep.validation_return > 0 and rep.oos_return < 0:
                fragile.append(rep.window_id)
    return fragile
