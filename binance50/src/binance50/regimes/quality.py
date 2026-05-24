from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeQualityError
from binance50.regimes.models import MarketRegime, RegimeClassification, RegimeRunResult


class RegimeQualityIssue(BaseModel):
    issue_type: str
    severity: str
    open_time: int
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegimeQualityReport(BaseModel):
    status: str
    row_count: int
    classification_count: int
    unknown_count: int
    transition_count: int
    transition_ratio: float
    missing_explanation_count: int
    confidence_out_of_range_count: int
    lookahead_risk_count: int
    issues: list[RegimeQualityIssue] = Field(default_factory=list)
    generated_at_utc: int


def detect_all_unknown(classifications: list[RegimeClassification]) -> bool:
    if not classifications:
        return False
    return all(c.regime == MarketRegime.unknown for c in classifications)


def detect_missing_explanations(
    classifications: list[RegimeClassification],
) -> list[RegimeQualityIssue]:
    issues = []
    for c in classifications:
        if not c.explanation:
            issues.append(
                RegimeQualityIssue(
                    issue_type="missing_explanation",
                    severity="error",
                    open_time=c.open_time,
                    message="Missing explanation",
                )
            )
    return issues


def detect_confidence_out_of_range(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeQualityIssue]:
    issues = []
    c_min = config.regimes.thresholds.min_regime_confidence
    c_max = config.regimes.thresholds.max_regime_confidence
    for c in classifications:
        if not (c_min <= c.confidence <= c_max):
            issues.append(
                RegimeQualityIssue(
                    issue_type="confidence_out_of_range",
                    severity="error",
                    open_time=c.open_time,
                    message=f"Confidence {c.confidence} out of bounds [{c_min}, {c_max}]",
                )
            )
    return issues


def detect_high_transition_ratio(
    classifications: list[RegimeClassification], transitions: list[Any], config: AppConfig
) -> list[RegimeQualityIssue]:
    if not classifications:
        return []
    ratio = len(transitions) / len(classifications)
    if ratio > config.regimes.quality.max_transition_ratio:
        return [
            RegimeQualityIssue(
                issue_type="high_transition_ratio",
                severity=(
                    "warning" if config.regimes.quality.warn_high_transition_ratio else "error"
                ),
                open_time=0,
                message=f"Transition ratio {ratio:.2f} exceeds max {config.regimes.quality.max_transition_ratio}",
            )
        ]
    return []


def detect_lookahead_risk(df: pd.DataFrame, config: AppConfig) -> list[RegimeQualityIssue]:
    invalid_cols = ["target", "label", "future_return", "next_close", "forward_return"]
    issues = []
    for col in invalid_cols:
        if col in df.columns:
            issues.append(
                RegimeQualityIssue(
                    issue_type="lookahead_risk",
                    severity="error",
                    open_time=0,
                    message=f"Leakage detected: column {col} found.",
                )
            )
    return issues


def build_regime_quality_report(
    result: RegimeRunResult, df: pd.DataFrame, config: AppConfig
) -> RegimeQualityReport:
    issues = []

    missing_exp = detect_missing_explanations(result.classifications)
    issues.extend(missing_exp)

    conf_issues = detect_confidence_out_of_range(result.classifications, config)
    issues.extend(conf_issues)

    trans_issues = detect_high_transition_ratio(result.classifications, result.transitions, config)
    issues.extend(trans_issues)

    lookahead_issues = detect_lookahead_risk(df, config)
    issues.extend(lookahead_issues)

    all_unknown = detect_all_unknown(result.classifications)
    if all_unknown and config.regimes.quality.warn_all_unknown:
        issues.append(
            RegimeQualityIssue(
                issue_type="all_unknown",
                severity=(
                    "warning"
                    if config.regimes.quality.warn_all_unknown
                    and not config.regimes.quality.reject_all_unknown
                    else "error"
                ),
                open_time=0,
                message="All classifications are unknown",
            )
        )

    error_issues = [i for i in issues if i.severity == "error"]
    status = "failed" if error_issues else "passed"

    return RegimeQualityReport(
        status=status,
        row_count=len(df),
        classification_count=len(result.classifications),
        unknown_count=sum(1 for c in result.classifications if c.regime == MarketRegime.unknown),
        transition_count=len(result.transitions),
        transition_ratio=len(result.transitions) / max(1, len(result.classifications)),
        missing_explanation_count=len(missing_exp),
        confidence_out_of_range_count=len(conf_issues),
        lookahead_risk_count=len(lookahead_issues),
        issues=issues,
        generated_at_utc=0,  # Placeholder
    )


def assert_regime_quality_passed(report: RegimeQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        raise RegimeQualityError(
            f"Regime quality failed with {len([i for i in report.issues if i.severity == 'error'])} errors"
        )
