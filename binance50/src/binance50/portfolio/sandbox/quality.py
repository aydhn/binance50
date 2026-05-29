import math
from datetime import datetime

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioSelectionRunResult


class PortfolioSandboxQualityIssue(BaseModel):
    issue_type: str
    severity: str
    candidate_id: str | None = None
    message: str
    metadata: dict = Field(default_factory=dict)


class PortfolioSandboxQualityReport(BaseModel):
    status: str
    run_id: str
    input_candidate_count: int
    eligible_candidate_count: int
    selected_candidate_count: int
    rejected_candidate_count: int
    missing_breakdown_count: int = 0
    missing_explanation_count: int = 0
    score_out_of_range_count: int = 0
    nan_inf_score_count: int = 0
    missing_hash_count: int = 0
    future_column_issue_count: int = 0
    forward_correlation_issue_count: int = 0
    production_write_intent_count: int = 0
    live_or_paper_intent_count: int = 0
    high_correlation_warning_count: int = 0
    high_concentration_warning_count: int = 0
    low_diversification_warning_count: int = 0
    issues: list[PortfolioSandboxQualityIssue] = Field(default_factory=list)
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)


def detect_missing_breakdowns(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    for cand in result.selected_candidates:
        if not cand.score_breakdown:
            issues.append(
                PortfolioSandboxQualityIssue(
                    issue_type="missing_breakdown",
                    severity="error",
                    candidate_id=cand.candidate_id,
                    message="Missing score breakdown",
                )
            )
    return issues


def detect_missing_explanations(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    for cand in result.selected_candidates:
        if not cand.explanation:
            issues.append(
                PortfolioSandboxQualityIssue(
                    issue_type="missing_explanation",
                    severity="error",
                    candidate_id=cand.candidate_id,
                    message="Missing explanation",
                )
            )
    return issues


def detect_score_out_of_range(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    for cand in result.selected_candidates:
        if not (0.0 <= cand.portfolio_score <= 100.0):
            issues.append(
                PortfolioSandboxQualityIssue(
                    issue_type="score_out_of_range",
                    severity="error",
                    candidate_id=cand.candidate_id,
                    message=f"Score {cand.portfolio_score} out of bounds (0-100)",
                )
            )
    return issues


def detect_nan_inf_scores(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    for cand in result.selected_candidates:
        if math.isnan(cand.portfolio_score) or math.isinf(cand.portfolio_score):
            issues.append(
                PortfolioSandboxQualityIssue(
                    issue_type="nan_inf_score",
                    severity="error",
                    candidate_id=cand.candidate_id,
                    message="NaN or Inf score detected",
                )
            )
    return issues


def detect_missing_hashes(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    if not result.reproducibility_report or "output_hash" not in result.reproducibility_report:
        issues.append(
            PortfolioSandboxQualityIssue(
                issue_type="missing_hash", severity="error", message="Reproducibility hash missing"
            )
        )
    return issues


def detect_forward_correlation(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    return []


def detect_future_columns(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    return []


def detect_production_write_intent(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    for cand in result.selected_candidates:
        if not cand.blocked_from_signal_engine or not cand.blocked_from_execution:
            issues.append(
                PortfolioSandboxQualityIssue(
                    issue_type="production_write_intent",
                    severity="error",
                    candidate_id=cand.candidate_id,
                    message="Blocked flags not set",
                )
            )
    return issues


def detect_live_or_paper_intent(
    result: PortfolioSelectionRunResult,
) -> list[PortfolioSandboxQualityIssue]:
    issues = []
    for cand in result.selected_candidates:
        if cand.intent.value in ["live", "paper"]:
            issues.append(
                PortfolioSandboxQualityIssue(
                    issue_type="live_or_paper_intent",
                    severity="error",
                    candidate_id=cand.candidate_id,
                    message="Live or paper intent detected",
                )
            )
    return issues


def build_portfolio_sandbox_quality_report(
    result: PortfolioSelectionRunResult, config: AppConfig
) -> PortfolioSandboxQualityReport:
    report = PortfolioSandboxQualityReport(
        status="passed",
        run_id=result.run_id,
        input_candidate_count=len(result.input_candidates),
        eligible_candidate_count=len(result.eligible_candidates),
        selected_candidate_count=len(result.selected_candidates),
        rejected_candidate_count=len(result.rejected_candidates),
    )

    issues = []
    issues.extend(detect_missing_breakdowns(result))
    issues.extend(detect_missing_explanations(result))
    issues.extend(detect_score_out_of_range(result))
    issues.extend(detect_nan_inf_scores(result))
    issues.extend(detect_missing_hashes(result))
    issues.extend(detect_forward_correlation(result))
    issues.extend(detect_future_columns(result))
    issues.extend(detect_production_write_intent(result))
    issues.extend(detect_live_or_paper_intent(result))

    # Update counts
    for issue in issues:
        setattr(
            report, f"{issue.issue_type}_count", getattr(report, f"{issue.issue_type}_count", 0) + 1
        )

    report.issues = issues

    if any(i.severity == "error" for i in issues):
        report.status = "failed"
    elif issues:
        report.status = "warnings"

    return report


def assert_portfolio_sandbox_quality_passed(
    report: PortfolioSandboxQualityReport, config: AppConfig
) -> None:
    q_config = config.portfolio_sandbox.quality

    if q_config.reject_no_candidates and report.input_candidate_count == 0:
        from binance50.core.exceptions import PortfolioSandboxQualityError

        raise PortfolioSandboxQualityError("No input candidates provided")

    if report.status == "failed":
        errors = [i.message for i in report.issues if i.severity == "error"]

        # Check specific rejection configs
        if report.missing_breakdown_count > 0 and q_config.reject_missing_breakdown:
            from binance50.core.exceptions import PortfolioSandboxQualityError

            raise PortfolioSandboxQualityError(f"Missing breakdowns: {errors[0]}")

        if report.missing_explanation_count > 0 and q_config.reject_missing_explanation:
            from binance50.core.exceptions import PortfolioSandboxQualityError

            raise PortfolioSandboxQualityError(f"Missing explanations: {errors[0]}")

        if report.score_out_of_range_count > 0 and q_config.reject_score_out_of_range:
            from binance50.core.exceptions import PortfolioSandboxQualityError

            raise PortfolioSandboxQualityError(f"Score out of range: {errors[0]}")

        if report.nan_inf_score_count > 0 and q_config.reject_nan_inf_scores:
            from binance50.core.exceptions import PortfolioSandboxQualityError

            raise PortfolioSandboxQualityError(f"NaN/Inf scores: {errors[0]}")

        if report.production_write_intent_count > 0 and q_config.reject_production_write_intent:
            from binance50.core.exceptions import PortfolioSandboxQualityError

            raise PortfolioSandboxQualityError(f"Production write intent: {errors[0]}")

        if report.live_or_paper_intent_count > 0 and q_config.reject_live_or_paper_intent:
            from binance50.core.exceptions import PortfolioSandboxQualityError

            raise PortfolioSandboxQualityError(f"Live/paper intent: {errors[0]}")
