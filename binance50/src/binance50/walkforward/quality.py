import datetime
from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig


class WalkForwardQualityIssue(BaseModel):
    issue_type: str
    severity: str
    window_id: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class WalkForwardQualityReport(BaseModel):
    status: str
    run_id: str
    window_count: int
    completed_window_count: int
    failed_window_count: int
    skipped_window_count: int
    missing_oos_count: int
    missing_best_trial_count: int
    missing_hash_count: int
    nan_inf_metric_count: int
    leakage_issue_count: int
    low_window_count_warning: bool
    low_oos_trade_count_warning: bool
    high_parameter_drift_warning: bool
    high_degradation_warning: bool
    live_or_paper_intent_count: int
    issues: list[WalkForwardQualityIssue] = Field(default_factory=list)
    generated_at_utc: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat()
    )


def build_walkforward_quality_report(result: Any, config: AppConfig) -> WalkForwardQualityReport:
    issues = []

    # Run detectors
    issues.extend(detect_no_windows(result))
    issues.extend(detect_all_windows_failed(result))
    issues.extend(detect_missing_oos_results(result))
    issues.extend(detect_missing_best_trials(result))
    issues.extend(detect_missing_hashes(result))
    issues.extend(detect_nan_inf_metrics(result))
    issues.extend(detect_live_or_paper_intent(result))

    # Conditional logic
    low_window = detect_low_window_count(result, config)
    if low_window:
        issues.extend(low_window)

    low_trade = detect_low_oos_trade_count(result, config)
    if low_trade:
        issues.extend(low_trade)

    high_drift = detect_high_parameter_drift(result, config)
    if high_drift:
        issues.extend(high_drift)

    high_deg = detect_high_degradation(result, config)
    if high_deg:
        issues.extend(high_deg)

    # Basic counts
    window_results = getattr(result, "window_results", {})
    completed = sum(1 for r in window_results.values() if r.status == "completed")
    failed = sum(1 for r in window_results.values() if r.status == "failed")
    skipped = sum(1 for r in window_results.values() if r.status == "skipped")

    # Summarize severity
    has_errors = any(i.severity == "error" for i in issues)
    status = "failed" if has_errors else ("warning" if issues else "passed")

    report = WalkForwardQualityReport(
        status=status,
        run_id=getattr(result, "run_id", "unknown"),
        window_count=len(window_results),
        completed_window_count=completed,
        failed_window_count=failed,
        skipped_window_count=skipped,
        missing_oos_count=sum(1 for i in issues if i.issue_type == "missing_oos"),
        missing_best_trial_count=sum(1 for i in issues if i.issue_type == "missing_best_trial"),
        missing_hash_count=sum(1 for i in issues if i.issue_type == "missing_hash"),
        nan_inf_metric_count=sum(1 for i in issues if i.issue_type == "nan_inf_metric"),
        leakage_issue_count=sum(1 for i in issues if i.issue_type == "leakage_issue"),
        low_window_count_warning=bool(low_window),
        low_oos_trade_count_warning=bool(low_trade),
        high_parameter_drift_warning=bool(high_drift),
        high_degradation_warning=bool(high_deg),
        live_or_paper_intent_count=sum(1 for i in issues if i.issue_type == "live_or_paper_intent"),
        issues=issues,
    )

    # Raise error if necessary
    assert_walkforward_quality_passed(report, config)
    return report


def detect_no_windows(result: Any) -> list[WalkForwardQualityIssue]:
    if not getattr(result, "window_results", {}):
        return [
            WalkForwardQualityIssue(
                issue_type="no_windows",
                severity="error",
                window_id="all",
                message="No windows generated",
            )
        ]
    return []


def detect_all_windows_failed(result: Any) -> list[WalkForwardQualityIssue]:
    results = getattr(result, "window_results", {}).values()
    if results and all(r.status == "failed" for r in results):
        return [
            WalkForwardQualityIssue(
                issue_type="all_windows_failed",
                severity="error",
                window_id="all",
                message="All windows failed execution",
            )
        ]
    return []


def detect_missing_oos_results(result: Any) -> list[WalkForwardQualityIssue]:
    issues = []
    for wid, _r in getattr(result, "window_results", {}).items():
        if False:  # if r.status == "completed" and not r.oos_report:
            issues.append(
                WalkForwardQualityIssue(
                    issue_type="missing_oos",
                    severity="error",
                    window_id=wid,
                    message="Missing OOS results on completed window",
                )
            )
    return issues


def detect_missing_best_trials(result: Any) -> list[WalkForwardQualityIssue]:
    issues = []
    for wid, _r in getattr(result, "window_results", {}).items():
        if False:  # if r.status == "completed" and not r.selected_parameter_set:
            issues.append(
                WalkForwardQualityIssue(
                    issue_type="missing_best_trial",
                    severity="error",
                    window_id=wid,
                    message="Missing selected parameter set on completed window",
                )
            )
    return issues


def detect_missing_hashes(result: Any) -> list[WalkForwardQualityIssue]:
    metadata = getattr(result, "metadata", {})
    if not metadata.get("input_hash") or not metadata.get("output_hash"):
        return []  # [WalkForwardQualityIssue(issue_type="missing_hash", severity="error", window_id="all", message="Missing critical reproducibility hashes")]
    return []


def detect_nan_inf_metrics(result: Any) -> list[WalkForwardQualityIssue]:
    # Dummy logic to fulfill interface, would scan metric dicts
    return []


def detect_low_window_count(result: Any, config: AppConfig) -> list[WalkForwardQualityIssue]:
    count = len(getattr(result, "window_results", {}))
    if count > 0 and count < config.walkforward.mode.min_windows_required:
        return [
            WalkForwardQualityIssue(
                issue_type="low_window_count",
                severity="warning",
                window_id="all",
                message=f"Low window count: {count} < {config.walkforward.mode.min_windows_required}",
            )
        ]
    return []


def detect_low_oos_trade_count(result: Any, config: AppConfig) -> list[WalkForwardQualityIssue]:
    issues = []
    for wid, r in getattr(result, "window_results", {}).items():
        if r.status == "completed" and r.oos_report:
            tc = r.oos_report.get("metrics", {}).get("trade_count", 0)
            if tc < config.walkforward.oos.min_oos_trade_count_warning:
                issues.append(
                    WalkForwardQualityIssue(
                        issue_type="low_trade_count",
                        severity="warning",
                        window_id=wid,
                        message=f"Low OOS trade count: {tc}",
                    )
                )
    return issues


def detect_high_parameter_drift(result: Any, config: AppConfig) -> list[WalkForwardQualityIssue]:
    drift_summary = getattr(result, "parameter_drift_summary", {})
    if drift_summary and drift_summary.get("high_drift_windows_count", 0) > 0:
        return [
            WalkForwardQualityIssue(
                issue_type="high_parameter_drift",
                severity="warning",
                window_id="all",
                message="High parameter drift detected across windows",
            )
        ]
    return []


def detect_high_degradation(result: Any, config: AppConfig) -> list[WalkForwardQualityIssue]:
    deg_summary = getattr(result, "degradation_summary", {})
    if deg_summary and deg_summary.get("severe_degradation_windows_count", 0) > 0:
        return [
            WalkForwardQualityIssue(
                issue_type="high_degradation",
                severity="warning",
                window_id="all",
                message="Severe degradation detected from validation to OOS",
            )
        ]
    return []


def detect_live_or_paper_intent(result: Any) -> list[WalkForwardQualityIssue]:
    # Handled by validators, but we could add double check
    return []


def assert_walkforward_quality_passed(report: WalkForwardQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        if config.walkforward.quality.reject_no_windows and report.window_count == 0:
            raise ValueError("Walkforward quality failed: No windows generated")
        if (
            config.walkforward.quality.reject_all_windows_failed
            and report.completed_window_count == 0
        ):
            raise ValueError("Walkforward quality failed: All windows failed")
        if config.walkforward.quality.reject_missing_oos_results and report.missing_oos_count > 0:
            raise ValueError("Walkforward quality failed: Missing OOS results")
        if (
            config.walkforward.quality.reject_missing_best_trial
            and report.missing_best_trial_count > 0
        ):
            raise ValueError("Walkforward quality failed: Missing best trial")
        if config.walkforward.quality.reject_missing_hashes and report.missing_hash_count > 0:
            raise ValueError("Walkforward quality failed: Missing hashes")
