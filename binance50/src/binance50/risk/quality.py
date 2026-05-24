from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import (
    RiskAssessment,
    RiskAssessmentStatus,
    RiskQualityIssue,
    RiskQualityReport,
    RiskRunResult,
)
from binance50.risk.validators import _EXECUTION_FIELD_BLACKLIST


def detect_missing_explanations(assessments: list[RiskAssessment]) -> list[RiskQualityIssue]:
    issues = []
    for a in assessments:
        if not a.explanation:
            issues.append(
                RiskQualityIssue(
                    issue_type="missing_explanation",
                    severity="warning",
                    assessment_id=a.assessment_id,
                    message="Risk assessment is missing an explanation",
                )
            )
    return issues


def detect_missing_breakdowns(assessments: list[RiskAssessment]) -> list[RiskQualityIssue]:
    issues = []
    for a in assessments:
        if not a.breakdown or not a.breakdown.components:
            issues.append(
                RiskQualityIssue(
                    issue_type="missing_breakdown",
                    severity="warning",
                    assessment_id=a.assessment_id,
                    message="Risk assessment is missing a breakdown",
                )
            )
    return issues


def detect_execution_fields(assessments: list[RiskAssessment]) -> list[RiskQualityIssue]:
    issues = []
    for a in assessments:
        dump = a.model_dump()
        for field in _EXECUTION_FIELD_BLACKLIST:
            if field in dump:
                issues.append(
                    RiskQualityIssue(
                        issue_type="execution_field_detected",
                        severity="critical",
                        assessment_id=a.assessment_id,
                        message=f"Risk assessment contains forbidden execution field: {field}",
                    )
                )
    return issues


def detect_order_language(assessments: list[RiskAssessment]) -> list[RiskQualityIssue]:
    issues = []
    order_words = ["buy", "sell", "order", "execute", "long", "short", "position"]
    for a in assessments:
        if a.explanation:
            text_lower = a.explanation.lower()
            for w in order_words:
                if w in text_lower:
                    issues.append(
                        RiskQualityIssue(
                            issue_type="order_language_detected",
                            severity="high",
                            assessment_id=a.assessment_id,
                            message=f"Risk explanation contains order-like language: {w}",
                        )
                    )
    return issues


def detect_score_out_of_range(
    assessments: list[RiskAssessment], config: AppConfig
) -> list[RiskQualityIssue]:
    issues = []
    for a in assessments:
        score = a.final_risk_score
        if score < 0.0 or score > config.risk.decision.max_risk_score:
            issues.append(
                RiskQualityIssue(
                    issue_type="score_out_of_range",
                    severity="high",
                    assessment_id=a.assessment_id,
                    message=f"Risk score {score} out of allowed range [0, {config.risk.decision.max_risk_score}]",
                )
            )
    return issues


def build_risk_quality_report(result_or_assessments: Any, config: AppConfig) -> RiskQualityReport:
    assessments = []
    if isinstance(result_or_assessments, list):
        assessments = result_or_assessments
    elif isinstance(result_or_assessments, RiskRunResult):
        assessments = result_or_assessments.assessments + result_or_assessments.rejected_assessments
    issues = []
    issues.extend(detect_missing_explanations(assessments))
    issues.extend(detect_missing_breakdowns(assessments))
    issues.extend(detect_execution_fields(assessments))
    issues.extend(detect_order_language(assessments))
    issues.extend(detect_score_out_of_range(assessments, config))
    if not assessments and config.risk.quality.warn_empty_assessment_set:
        issues.append(
            RiskQualityIssue(
                issue_type="empty_assessment_set",
                severity="warning",
                message="No risk assessments were provided for the report.",
            )
        )
    return RiskQualityReport(
        status=(
            "failed"
            if any(i.severity in ["high", "critical", "blocked"] for i in issues)
            else "passed"
        ),
        assessment_count=len(assessments),
        rejected_count=sum(
            1 for a in assessments if a.status == RiskAssessmentStatus.rejected_by_risk
        ),
        blocked_count=sum(
            1 for a in assessments if a.status == RiskAssessmentStatus.blocked_by_policy
        ),
        needs_review_count=sum(
            1 for a in assessments if a.status == RiskAssessmentStatus.needs_review
        ),
        approved_future_backtest_count=sum(
            1 for a in assessments if a.status == RiskAssessmentStatus.approved_for_future_backtest
        ),
        approved_paper_review_count=sum(
            1 for a in assessments if a.status == RiskAssessmentStatus.approved_for_paper_review
        ),
        missing_explanation_count=len([i for i in issues if i.issue_type == "missing_explanation"]),
        missing_breakdown_count=len([i for i in issues if i.issue_type == "missing_breakdown"]),
        execution_field_count=len(
            [i for i in issues if i.issue_type == "execution_field_detected"]
        ),
        order_language_count=len([i for i in issues if i.issue_type == "order_language_detected"]),
        score_out_of_range_count=len([i for i in issues if i.issue_type == "score_out_of_range"]),
        issues=issues,
    )


def assert_risk_quality_passed(report: RiskQualityReport, config: AppConfig) -> None:
    from binance50.core.exceptions import RiskQualityError

    for issue in report.issues:
        if (
            issue.issue_type == "empty_assessment_set"
            and config.risk.quality.reject_empty_assessment_set
        ):
            raise RiskQualityError("Empty risk assessments set rejected by quality config.")
        if (
            issue.issue_type == "missing_explanation"
            and config.risk.quality.reject_missing_explanation
        ):
            raise RiskQualityError(f"Missing explanation rejected: {issue.message}")
        if issue.issue_type == "missing_breakdown" and config.risk.quality.reject_missing_breakdown:
            raise RiskQualityError(f"Missing breakdown rejected: {issue.message}")
        if (
            issue.issue_type == "score_out_of_range"
            and config.risk.quality.reject_score_out_of_range
        ):
            raise RiskQualityError(f"Score out of range rejected: {issue.message}")
        if (
            issue.issue_type == "execution_field_detected"
            and config.risk.quality.reject_execution_fields
        ):
            raise RiskQualityError(f"Execution field rejected: {issue.message}")
        if (
            issue.issue_type == "order_language_detected"
            and config.risk.quality.reject_order_like_language
        ):
            raise RiskQualityError(f"Order-like language rejected: {issue.message}")
