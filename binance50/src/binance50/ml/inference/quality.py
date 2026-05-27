from typing import Any, Dict, List
import datetime
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLInferenceRunResult
from binance50.core.exceptions import MLInferenceQualityError

class MLInferenceQualityIssue(BaseModel):
    issue_type: str
    severity: str
    prediction_id: str = "N/A"
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLInferenceQualityReport(BaseModel):
    status: str = "pending"
    run_id: str
    prediction_count: int
    no_model_loaded_count: int = 0
    untrusted_artifact_count: int = 0
    hash_mismatch_count: int = 0
    schema_mismatch_count: int = 0
    missing_model_card_count: int = 0
    missing_dataset_manifest_count: int = 0
    missing_prediction_count: int = 0
    probability_out_of_range_count: int = 0
    probability_sum_invalid_count: int = 0
    nan_inf_output_count: int = 0
    missing_manifest_count: int = 0
    missing_hash_count: int = 0
    uncalibrated_probability_warning_count: int = 0
    labels_missing_for_calibration_warning_count: int = 0
    single_class_collapse_warning_count: int = 0
    low_confidence_warning_count: int = 0
    feature_drift_warning_count: int = 0
    live_or_paper_intent_count: int = 0
    issues: List[MLInferenceQualityIssue] = Field(default_factory=list)
    generated_at_utc: str

def build_ml_inference_quality_report(result: MLInferenceRunResult, config: AppConfig) -> MLInferenceQualityReport:
    issues = []

    no_model = 1 if not result.model_load_report else 0
    if no_model: issues.append(MLInferenceQualityIssue(issue_type="no_model_loaded", severity="error", message="Model load report missing"))

    untrusted = 1 if result.model_load_report and not result.model_load_report.trusted_artifact else 0
    if untrusted: issues.append(MLInferenceQualityIssue(issue_type="untrusted_artifact", severity="error", message="Artifact not trusted"))

    hash_mismatch = 1 if result.model_load_report and not result.model_load_report.hash_verified else 0
    if hash_mismatch: issues.append(MLInferenceQualityIssue(issue_type="hash_mismatch", severity="error", message="Hash mismatch"))

    missing_preds = 1 if not result.predictions else 0
    if missing_preds: issues.append(MLInferenceQualityIssue(issue_type="missing_predictions", severity="error", message="No predictions generated"))

    live_intent = sum(1 for p in result.predictions if p.prediction_intent in ["live", "paper"])
    if live_intent: issues.append(MLInferenceQualityIssue(issue_type="live_or_paper_intent", severity="error", message="Live/Paper intent detected"))

    # Determine status
    status = "passed"
    if issues:
        status = "failed" if any(i.severity == "error" for i in issues) else "warnings"

    return MLInferenceQualityReport(
        status=status,
        run_id=result.run_id,
        prediction_count=len(result.predictions),
        no_model_loaded_count=no_model,
        untrusted_artifact_count=untrusted,
        hash_mismatch_count=hash_mismatch,
        missing_prediction_count=missing_preds,
        live_or_paper_intent_count=live_intent,
        issues=issues,
        generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

def assert_ml_inference_quality_passed(report: MLInferenceQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        raise MLInferenceQualityError(f"Quality checks failed: {len([i for i in report.issues if i.severity == 'error'])} errors")
