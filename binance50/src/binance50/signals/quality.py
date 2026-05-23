import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from binance50.config.models import AppConfig
from binance50.signals.models import ScoredSignalCandidate, SignalScoringResult


class SignalQualityIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    issue_type: str
    severity: str
    scored_signal_id: str | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SignalQualityReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    scored_count: int
    rejected_count: int
    conflict_count: int
    high_conflict_ratio: bool
    missing_breakdown_count: int
    missing_explanation_count: int
    out_of_range_score_count: int
    order_language_count: int
    execution_intent_count: int
    issues: list[SignalQualityIssue] = Field(default_factory=list)
    generated_at_utc: datetime.datetime | int


def detect_score_out_of_range(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    issues: list[SignalQualityIssue] = []
    min_score = config.signals.scoring.min_score
    max_score = config.signals.scoring.max_score
    for s in scored:
        if s.score < min_score or s.score > max_score:
            issues.append(SignalQualityIssue(
                issue_type="score_out_of_range",
                severity="error" if config.signals.quality.reject_score_out_of_range else "warning",
                scored_signal_id=s.scored_signal_id,
                message=f"Score {s.score} is out of bounds [{min_score}, {max_score}]"
            ))
    return issues


def detect_missing_breakdowns(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    issues: list[SignalQualityIssue] = []
    for s in scored:
        if not s.score_breakdown:
            issues.append(SignalQualityIssue(
                issue_type="missing_breakdown",
                severity="error" if config.signals.quality.reject_missing_breakdown else "warning",
                scored_signal_id=s.scored_signal_id,
                message="Score breakdown is missing"
            ))
    return issues


def detect_missing_explanations(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    issues: list[SignalQualityIssue] = []
    for s in scored:
        if not s.explanation:
            issues.append(SignalQualityIssue(
                issue_type="missing_explanation",
                severity="error" if config.signals.quality.reject_missing_explanation else "warning",
                scored_signal_id=s.scored_signal_id,
                message="Score explanation is missing"
            ))
    return issues


def detect_order_language(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    issues: list[SignalQualityIssue] = []
    forbidden_terms = [
        "buy now", "sell now", "execute", "place order", "market order",
        "open long", "open short", "close position", "emir gönder",
        "al emri", "sat emri", "long aç", "short aç"
    ]
    for s in scored:
        if s.explanation:
            text = s.explanation.lower()
            for term in forbidden_terms:
                if term in text:
                    issues.append(SignalQualityIssue(
                        issue_type="order_language_detected",
                        severity="error" if config.signals.quality.reject_order_language else "warning",
                        scored_signal_id=s.scored_signal_id,
                        message=f"Actionable language '{term}' detected in explanation"
                    ))
                    break
    return issues


def detect_execution_intent(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    issues: list[SignalQualityIssue] = []
    for s in scored:
        intent_val = s.intent.value.lower()
        if "execution" in intent_val or "order" in intent_val and "no" not in intent_val:
            issues.append(SignalQualityIssue(
                issue_type="execution_intent",
                severity="error" if config.signals.quality.reject_execution_intent else "warning",
                scored_signal_id=s.scored_signal_id,
                message=f"Execution intent '{s.intent.value}' detected"
            ))
    return issues


def detect_high_conflict_ratio(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    if not scored:
        return []

    conflict_count = sum(1 for s in scored if s.conflicted)
    ratio = conflict_count / len(scored)

    if config.signals.quality.warn_high_conflict_ratio and ratio > config.signals.quality.max_conflict_ratio:
        return [SignalQualityIssue(
            issue_type="high_conflict_ratio",
            severity="warning",
            message=f"High conflict ratio: {ratio:.2f} > {config.signals.quality.max_conflict_ratio:.2f}",
            metadata={"conflict_count": conflict_count, "total": len(scored), "ratio": ratio}
        )]
    return []


def detect_single_plugin_high_scores(scored: list[ScoredSignalCandidate], config: AppConfig) -> list[SignalQualityIssue]:
    issues: list[SignalQualityIssue] = []
    if not config.signals.quality.warn_single_plugin_high_score:
        return issues

    threshold = config.signals.quality.max_single_plugin_score_without_confluence
    for s in scored:
        if s.score > threshold and not s.confluence_group_id:
            issues.append(SignalQualityIssue(
                issue_type="single_plugin_high_score",
                severity="warning",
                scored_signal_id=s.scored_signal_id,
                message=f"High score ({s.score}) achieved without confluence support",
                metadata={"score": s.score, "threshold": threshold}
            ))
    return issues


def build_signal_quality_report(result_or_scored: SignalScoringResult | list[ScoredSignalCandidate], config: AppConfig) -> SignalQualityReport:
    scored_candidates = result_or_scored.scored_candidates if isinstance(result_or_scored, SignalScoringResult) else result_or_scored

    issues: list[SignalQualityIssue] = []
    issues.extend(detect_score_out_of_range(scored_candidates, config))
    issues.extend(detect_missing_breakdowns(scored_candidates, config))
    issues.extend(detect_missing_explanations(scored_candidates, config))
    issues.extend(detect_order_language(scored_candidates, config))
    issues.extend(detect_execution_intent(scored_candidates, config))
    issues.extend(detect_high_conflict_ratio(scored_candidates, config))
    issues.extend(detect_single_plugin_high_scores(scored_candidates, config))

    error_count = sum(1 for i in issues if i.severity == "error")
    status = "failed" if error_count > 0 else "passed"

    return SignalQualityReport(
        status=status,
        scored_count=len(scored_candidates),
        rejected_count=len(result_or_scored.rejected_candidates) if isinstance(result_or_scored, SignalScoringResult) else 0,
        conflict_count=sum(1 for s in scored_candidates if s.conflicted),
        high_conflict_ratio=any(i.issue_type == "high_conflict_ratio" for i in issues),
        missing_breakdown_count=sum(1 for i in issues if i.issue_type == "missing_breakdown"),
        missing_explanation_count=sum(1 for i in issues if i.issue_type == "missing_explanation"),
        out_of_range_score_count=sum(1 for i in issues if i.issue_type == "score_out_of_range"),
        order_language_count=sum(1 for i in issues if i.issue_type == "order_language_detected"),
        execution_intent_count=sum(1 for i in issues if i.issue_type == "execution_intent"),
        issues=issues,
        generated_at_utc=int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
    )


def assert_signal_quality_passed(report: SignalQualityReport, config: AppConfig) -> None:
    if report.status != "passed":
        error_msgs = [i.message for i in report.issues if i.severity == "error"]
        from binance50.core.exceptions import SignalQualityError
        raise SignalQualityError(f"Signal quality checks failed: {'; '.join(error_msgs)}")
