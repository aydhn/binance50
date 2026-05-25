from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindowResult


class WalkForwardDegradationReport(BaseModel):
    window_id: str
    validation_score: float
    oos_score: float
    validation_to_oos_score_drop: float
    validation_return: float
    oos_return: float
    validation_to_oos_return_drop_pct: float
    validation_sharpe: float
    oos_sharpe: float
    validation_to_oos_sharpe_drop: float
    severe_degradation: bool
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def compute_window_degradation(
    window_result: WalkForwardWindowResult, config: AppConfig
) -> WalkForwardDegradationReport:
    val_report = window_result.validation_report or {}
    oos_report = window_result.oos_report or {}

    val_metrics = val_report.get("metrics", {})
    oos_metrics = oos_report.get("metrics", {})

    val_score = val_metrics.get(config.walkforward.optimizer.select_best_by, 0.0)
    oos_score = oos_metrics.get(config.walkforward.optimizer.select_best_by, 0.0)

    val_ret = val_metrics.get("cagr", val_metrics.get("total_return_pct", 0.0))
    oos_ret = oos_metrics.get("cagr", oos_metrics.get("total_return_pct", 0.0))

    val_sharpe = val_metrics.get("sharpe", 0.0)
    oos_sharpe = oos_metrics.get("sharpe", 0.0)

    score_drop = val_score - oos_score
    ret_drop_pct = ((val_ret - oos_ret) / max(abs(val_ret), 1e-5)) * 100 if val_ret > 0 else 0.0
    sharpe_drop = val_sharpe - oos_sharpe

    wf_config = config.walkforward.degradation

    severe = (
        score_drop > wf_config.max_validation_to_oos_score_drop
        or ret_drop_pct > wf_config.max_validation_to_oos_return_drop_pct
        or sharpe_drop > wf_config.max_validation_to_oos_sharpe_drop
    )

    warnings = []
    if severe and wf_config.warn_severe_degradation:
        warnings.append(f"Severe degradation detected for window {window_result.window_id}")

    return WalkForwardDegradationReport(
        window_id=window_result.window_id,
        validation_score=val_score,
        oos_score=oos_score,
        validation_to_oos_score_drop=score_drop,
        validation_return=val_ret,
        oos_return=oos_ret,
        validation_to_oos_return_drop_pct=ret_drop_pct,
        validation_sharpe=val_sharpe,
        oos_sharpe=oos_sharpe,
        validation_to_oos_sharpe_drop=sharpe_drop,
        severe_degradation=severe,
        warnings=warnings,
    )


def compute_degradation_for_all_windows(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> list[WalkForwardDegradationReport]:
    reports = []
    for res in window_results.values():
        if res.status == "completed":
            reports.append(compute_window_degradation(res, config))
    return reports


def summarize_degradation(
    reports: list[WalkForwardDegradationReport], config: AppConfig
) -> dict[str, Any]:
    if not reports:
        return {}

    severe_count = sum(1 for r in reports if r.severe_degradation)
    avg_score_drop = sum(r.validation_to_oos_score_drop for r in reports) / len(reports)

    return {
        "severe_degradation_windows_count": severe_count,
        "average_score_drop": avg_score_drop,
        "classification": classify_degradation(reports, config),
    }


def classify_degradation(reports: list[WalkForwardDegradationReport], config: AppConfig) -> str:
    if not reports:
        return "unknown"
    severe_ratio = sum(1 for r in reports if r.severe_degradation) / len(reports)
    if severe_ratio > 0.5:
        return "high_degradation"
    elif severe_ratio > 0.2:
        return "moderate_degradation"
    return "stable"
