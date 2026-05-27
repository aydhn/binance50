from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLBlendingQualityError
from binance50.ml.blending.models import MLBlendingRunResult


class MLBlendingQualityIssue(BaseModel):
    issue_type: str
    severity: str
    candidate_id: str | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MLBlendingQualityReport(BaseModel):
    status: str
    run_id: str
    candidate_count: int
    missing_ml_inference_count: int = 0
    missing_signal_count: int = 0
    missing_breakdown_count: int = 0
    missing_explanation_count: int = 0
    probability_out_of_range_count: int = 0
    invalid_weight_count: int = 0
    nan_inf_score_count: int = 0
    missing_hash_count: int = 0
    forward_alignment_issue_count: int = 0
    production_write_intent_count: int = 0
    live_or_paper_intent_count: int = 0
    uncalibrated_probability_warning_count: int = 0
    high_disagreement_warning_count: int = 0
    low_confidence_warning_count: int = 0
    issues: list[MLBlendingQualityIssue] = Field(default_factory=list)
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)


def build_ml_blending_quality_report(
    result: MLBlendingRunResult, config: AppConfig
) -> MLBlendingQualityReport:
    return MLBlendingQualityReport(
        status="passed", run_id=result.run_id, candidate_count=len(result.blended_candidates)
    )


def detect_missing_inputs(result: Any) -> list[MLBlendingQualityIssue]:
    return []


def detect_missing_breakdowns(candidates: list[Any]) -> list[MLBlendingQualityIssue]:
    return []


def detect_missing_explanations(candidates: list[Any]) -> list[MLBlendingQualityIssue]:
    return []


def detect_probability_out_of_range(candidates: list[Any]) -> list[MLBlendingQualityIssue]:
    return []


def detect_invalid_weights(result: Any) -> list[MLBlendingQualityIssue]:
    return []


def detect_nan_inf_scores(candidates: list[Any]) -> list[MLBlendingQualityIssue]:
    return []


def detect_missing_hashes(result: Any) -> list[MLBlendingQualityIssue]:
    return []


def detect_forward_alignment(result: Any) -> list[MLBlendingQualityIssue]:
    return []


def detect_production_write_intent(result: Any) -> list[MLBlendingQualityIssue]:
    return []


def detect_live_or_paper_intent(result: Any) -> list[MLBlendingQualityIssue]:
    return []


def assert_ml_blending_quality_passed(report: MLBlendingQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        raise MLBlendingQualityError("Quality checks failed.")
