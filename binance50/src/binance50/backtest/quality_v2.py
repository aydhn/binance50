import math
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from binance50.backtest.analytics.report_models import BacktestReportPack
from binance50.config.models import AppConfig


class BacktestReportQualityIssue(BaseModel):
    issue_type: str
    severity: str
    section: str
    message: str
    metadata: dict[str, Any] = {}


class BacktestReportQualityReport(BaseModel):
    status: str
    report_id: str
    section_count: int
    metric_count: int
    nan_inf_metric_count: int
    missing_disclaimer_count: int
    missing_hash_count: int
    low_observation_warning_count: int
    low_trade_warning_count: int
    live_claim_count: int
    issues: list[BacktestReportQualityIssue]
    generated_at_utc: datetime | str


def detect_nan_inf_metrics(pack: BacktestReportPack) -> list[BacktestReportQualityIssue]:
    issues = []
    if not pack.advanced_metrics:
        return issues

    metrics = pack.advanced_metrics.model_dump(exclude={"run_id", "warnings", "metadata"})
    for k, v in metrics.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            issues.append(
                BacktestReportQualityIssue(
                    issue_type="nan_inf_metric",
                    severity="error",
                    section="advanced_metrics",
                    message=f"Metric {k} is NaN or Inf",
                )
            )
    return issues


def detect_missing_sections(pack: BacktestReportPack) -> list[BacktestReportQualityIssue]:
    issues = []
    # Simplified check
    if not pack.summary:
        issues.append(
            BacktestReportQualityIssue(
                issue_type="missing_section",
                severity="warning",
                section="summary",
                message="Summary section is empty",
            )
        )
    return issues


def detect_missing_disclaimer(pack: BacktestReportPack) -> list[BacktestReportQualityIssue]:
    issues = []
    if not pack.disclaimer:
        issues.append(
            BacktestReportQualityIssue(
                issue_type="missing_disclaimer",
                severity="error",
                section="disclaimer",
                message="Disclaimer is missing",
            )
        )
    return issues


def detect_missing_hashes(pack: BacktestReportPack) -> list[BacktestReportQualityIssue]:
    issues = []
    if not pack.input_hash or not pack.config_hash or not pack.report_hash:
        issues.append(
            BacktestReportQualityIssue(
                issue_type="missing_hash",
                severity="error",
                section="metadata",
                message="One or more hashes are missing",
            )
        )
    return issues


def detect_live_performance_claims(pack: BacktestReportPack) -> list[BacktestReportQualityIssue]:
    issues = []
    forbidden_phrases = ["guaranteed profit", "kesin kazanç", "live proven"]

    # Check disclaimer specifically, but could check whole report
    text = str(pack.disclaimer).lower()
    for phrase in forbidden_phrases:
        if phrase in text:
            issues.append(
                BacktestReportQualityIssue(
                    issue_type="live_performance_claim",
                    severity="error",
                    section="disclaimer",
                    message=f"Live performance claim detected: '{phrase}'",
                )
            )
    return issues


def detect_low_observation_warnings(pack: BacktestReportPack) -> list[BacktestReportQualityIssue]:
    issues = []
    if pack.advanced_metrics and pack.advanced_metrics.warnings:
        for w in pack.advanced_metrics.warnings:
            if "low observation" in w.lower() or "low trade" in w.lower():
                issues.append(
                    BacktestReportQualityIssue(
                        issue_type="low_observation_warning",
                        severity="warning",
                        section="advanced_metrics",
                        message=w,
                    )
                )
    return issues


def build_backtest_report_quality(
    pack: BacktestReportPack, config: AppConfig
) -> BacktestReportQualityReport:
    issues = []
    issues.extend(detect_nan_inf_metrics(pack))
    issues.extend(detect_missing_sections(pack))
    issues.extend(detect_missing_disclaimer(pack))
    issues.extend(detect_missing_hashes(pack))
    issues.extend(detect_live_performance_claims(pack))
    issues.extend(detect_low_observation_warnings(pack))

    status = "passed"
    for issue in issues:
        if issue.severity == "error":
            status = "failed"
            break

    return BacktestReportQualityReport(
        status=status,
        report_id=pack.report_id,
        section_count=len(pack.model_dump().keys()),
        metric_count=len(pack.advanced_metrics.model_dump().keys()) if pack.advanced_metrics else 0,
        nan_inf_metric_count=sum(1 for i in issues if i.issue_type == "nan_inf_metric"),
        missing_disclaimer_count=sum(1 for i in issues if i.issue_type == "missing_disclaimer"),
        missing_hash_count=sum(1 for i in issues if i.issue_type == "missing_hash"),
        low_observation_warning_count=sum(
            1 for i in issues if i.issue_type == "low_observation_warning"
        ),
        low_trade_warning_count=sum(1 for i in issues if "low trade" in i.message.lower()),
        live_claim_count=sum(1 for i in issues if i.issue_type == "live_performance_claim"),
        issues=issues,
        generated_at_utc=datetime.now(UTC),
    )


def assert_backtest_report_quality_passed(
    report: BacktestReportQualityReport, config: AppConfig
) -> None:
    if report.status != "passed":
        from binance50.core.exceptions import BacktestReportQualityError

        raise BacktestReportQualityError(
            f"Report quality failed with "
            f"{len([i for i in report.issues if i.severity == 'error'])} "
            "errors"
        )
