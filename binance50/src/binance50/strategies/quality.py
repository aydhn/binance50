import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from binance50.config.models import AppConfig
from binance50.strategies.candidates import detect_conflicting_candidates
from binance50.strategies.models import SignalCandidate, StrategyCandidateStatus


class StrategyQualityIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    issue_type: str
    severity: str
    plugin_name: str | None = None
    candidate_id: str | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StrategyQualityReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    candidate_count: int
    rejected_count: int
    plugin_count: int
    issues: list[StrategyQualityIssue] = Field(default_factory=list)
    conflicting_candidates: int = 0
    duplicate_candidates: int = 0
    missing_explanations: int = 0
    order_language_hits: int = 0
    generated_at_utc: datetime.datetime | int


def detect_duplicate_candidates(candidates: list[SignalCandidate]) -> list[StrategyQualityIssue]:
    seen = set()
    issues = []
    for c in candidates:
        if c.candidate_id in seen:
            issues.append(
                StrategyQualityIssue(
                    issue_type="duplicate_candidate",
                    severity="warning",
                    plugin_name=c.plugin_name,
                    candidate_id=c.candidate_id,
                    message="Duplicate candidate ID detected",
                )
            )
        seen.add(c.candidate_id)
    return issues


def detect_missing_explanations(candidates: list[SignalCandidate]) -> list[StrategyQualityIssue]:
    issues = []
    for c in candidates:
        if c.status == StrategyCandidateStatus.candidate and not c.explanation.summary:
            issues.append(
                StrategyQualityIssue(
                    issue_type="missing_explanation",
                    severity="error",
                    plugin_name=c.plugin_name,
                    candidate_id=c.candidate_id,
                    message="Missing explanation summary",
                )
            )
    return issues


def detect_order_language_in_candidates(
    candidates: list[SignalCandidate],
) -> list[StrategyQualityIssue]:
    from binance50.strategies.validators import detect_order_like_language

    issues = []
    for c in candidates:
        if detect_order_like_language(c.explanation.summary) or detect_order_like_language(
            c.explanation.human_readable
        ):
            issues.append(
                StrategyQualityIssue(
                    issue_type="actionable_language",
                    severity="error",
                    plugin_name=c.plugin_name,
                    candidate_id=c.candidate_id,
                    message="Order-like language detected in candidate explanation",
                )
            )
    return issues


def build_strategy_quality_report(
    candidates: list[SignalCandidate], config: AppConfig
) -> StrategyQualityReport:
    import time

    issues = []

    if not candidates:
        severity = "error" if config.strategies.quality.reject_empty_candidate_set else "warning"
        issues.append(
            StrategyQualityIssue(
                issue_type="empty_candidate_set",
                severity=severity,
                message="No candidates generated",
            )
        )

    dupes = detect_duplicate_candidates(candidates)
    if dupes and config.strategies.quality.reject_duplicate_candidates:
        for d in dupes:
            issues.append(d.model_copy(update={"severity": "error"}))
    else:
        issues.extend(dupes)

    missing_exp = detect_missing_explanations(candidates)
    if missing_exp and config.strategies.quality.reject_missing_explanation:
        issues.extend(missing_exp)

    lang_issues = detect_order_language_in_candidates(candidates)
    if lang_issues and config.strategies.quality.reject_order_like_language:
        issues.extend(lang_issues)

    conflicts = detect_conflicting_candidates(candidates)
    if conflicts and config.strategies.quality.warn_conflicting_candidates:
        for c in conflicts:
            issues.append(
                StrategyQualityIssue(
                    issue_type="conflicting_candidates",
                    severity="warning",
                    message=f"Conflicting directions at {c['open_time']}",
                    metadata=c,
                )
            )

    active = [c for c in candidates if c.status == StrategyCandidateStatus.candidate]
    rejected = [c for c in candidates if c.status == StrategyCandidateStatus.rejected]
    plugins = {c.plugin_name for c in candidates}

    status = "pass"
    if any(i.severity == "error" for i in issues):
        status = "fail"

    return StrategyQualityReport(
        status=status,
        candidate_count=len(active),
        rejected_count=len(rejected),
        plugin_count=len(plugins),
        issues=issues,
        conflicting_candidates=len(conflicts),
        duplicate_candidates=len(dupes),
        missing_explanations=len(missing_exp),
        order_language_hits=len(lang_issues),
        generated_at_utc=int(time.time() * 1000),
    )


def assert_strategy_quality_passed(report: StrategyQualityReport, config: AppConfig) -> None:
    if report.status == "fail":
        from binance50.core.exceptions import StrategyQualityError

        errors = [i.message for i in report.issues if i.severity == "error"]
        raise StrategyQualityError(f"Strategy quality failed: {errors}")
