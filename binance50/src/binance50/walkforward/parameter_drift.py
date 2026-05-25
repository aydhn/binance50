from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindowResult


class ParameterDriftReport(BaseModel):
    window_id: str
    parameter_changes: dict[str, dict[str, Any]]
    numeric_drift_score: float
    categorical_drift_score: float
    total_drift_score: float
    high_drift: bool
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def compute_parameter_drift_between_windows(
    prev_params: dict[str, Any], curr_params: dict[str, Any], config: AppConfig
) -> ParameterDriftReport:
    changes = {}
    numeric_drift = 0.0
    categorical_drift = 0.0
    num_count = 0
    cat_count = 0

    all_keys = set(prev_params.keys()).union(set(curr_params.keys()))

    for k in all_keys:
        prev_val = prev_params.get(k)
        curr_val = curr_params.get(k)

        if prev_val == curr_val:
            continue

        changes[k] = {"from": prev_val, "to": curr_val}

        is_num = isinstance(prev_val, (int, float)) or isinstance(curr_val, (int, float))
        if isinstance(prev_val, bool) or isinstance(curr_val, bool):
            is_num = False

        if is_num:
            # Simple numeric distance approximation (real implementation would use parameter ranges)
            dist = normalize_numeric_parameter_distance(prev_val, curr_val, {})
            numeric_drift += dist
            num_count += 1
        else:
            categorical_drift += 1.0
            cat_count += 1

    num_score = numeric_drift / num_count if num_count > 0 else 0.0
    cat_score = categorical_drift / cat_count if cat_count > 0 else 0.0

    total_score = (
        (num_score + cat_score) / 2
        if (num_count > 0 and cat_count > 0)
        else max(num_score, cat_score)
    )

    high_drift = total_score > config.walkforward.parameter_drift.high_drift_threshold
    warnings = []
    if high_drift and config.walkforward.parameter_drift.warn_high_drift:
        warnings.append(f"High parameter drift detected: {total_score:.2f}")

    return ParameterDriftReport(
        window_id="current",  # Will be overwritten in series
        parameter_changes=changes,
        numeric_drift_score=num_score,
        categorical_drift_score=cat_score,
        total_drift_score=total_score,
        high_drift=high_drift,
        warnings=warnings,
    )


def compute_parameter_drift_series(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> list[ParameterDriftReport]:
    sorted_results = sorted(window_results.values(), key=lambda r: r.window_id)
    reports = []

    for i in range(1, len(sorted_results)):
        prev = sorted_results[i - 1]
        curr = sorted_results[i]

        prev_params = prev.selected_parameter_set or {}
        curr_params = curr.selected_parameter_set or {}

        report = compute_parameter_drift_between_windows(prev_params, curr_params, config)
        report.window_id = curr.window_id
        reports.append(report)

    return reports


def summarize_parameter_drift(
    reports: list[ParameterDriftReport], config: AppConfig
) -> dict[str, Any]:
    if not reports:
        return {}

    avg_total = sum(r.total_drift_score for r in reports) / len(reports)
    high_drift_count = sum(1 for r in reports if r.high_drift)

    return {
        "average_drift_score": avg_total,
        "high_drift_windows_count": high_drift_count,
        "stability_class": classify_parameter_stability(avg_total, config),
    }


def normalize_numeric_parameter_distance(
    value_a: Any, value_b: Any, metadata: dict[str, Any]
) -> float:
    # Fallback absolute difference relative to max if metadata bounds unavailable
    if value_a is None or value_b is None:
        return 1.0
    val_a = float(value_a)
    val_b = float(value_b)
    denom = max(abs(val_a), abs(val_b))
    if denom == 0:
        return 0.0
    return abs(val_a - val_b) / denom


def classify_parameter_stability(drift_score: float, config: AppConfig) -> str:
    if drift_score < 0.2:
        return "stable"
    elif drift_score < config.walkforward.parameter_drift.high_drift_threshold:
        return "moderate"
    else:
        return "unstable"
