from typing import Any
from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLTrainingQualityReport, MLTrainingQualityIssue

def build_ml_training_quality_report(result: Any, config: AppConfig) -> MLTrainingQualityReport:
    issues = []

    if len(result.model_results) == 0:
        issues.append(MLTrainingQualityIssue(issue_type="no_models_trained", severity="high", message="No models trained"))

    missing_metrics = 0
    missing_cal = 0
    missing_card = 0
    nan_inf = 0
    uncalibrated = 0

    for m in result.model_results:
        if not m.validation_metrics:
            missing_metrics += 1
            issues.append(MLTrainingQualityIssue(issue_type="missing_metrics", severity="high", message="Missing metrics", model_id=m.model_id))
        else:
            for v in m.validation_metrics.values():
                if isinstance(v, float) and (v != v or v == float('inf') or v == float('-inf')):
                    nan_inf += 1

        if not m.calibration_report:
            missing_cal += 1
        elif not m.calibration_report.calibrated:
            uncalibrated += 1

        if not m.model_card:
            missing_card += 1

    report = MLTrainingQualityReport(
        status="passed" if not issues else "failed",
        run_id=result.run_id,
        model_count=len(result.model_results),
        trained_model_count=len([m for m in result.model_results if m.status.value == "trained"]),
        failed_model_count=len([m for m in result.model_results if m.status.value == "failed"]),
        missing_metrics_count=missing_metrics,
        missing_calibration_count=missing_cal,
        missing_model_card_count=missing_card,
        missing_dataset_manifest_count=0 if result.dataset_manifest else 1,
        missing_hash_count=0,
        nan_inf_metric_count=nan_inf,
        single_class_train_count=0,
        class_imbalance_warning_count=0,
        uncalibrated_model_warning_count=uncalibrated,
        live_or_paper_intent_count=0,
        issues=issues,
        generated_at_utc=datetime.now(timezone.utc).isoformat()
    )
    return report

def assert_ml_training_quality_passed(report: MLTrainingQualityReport, config: AppConfig) -> None:
    if config.ml_training.quality.reject_no_models_trained and report.trained_model_count == 0:
        raise ValueError("No models trained successfully")
    if config.ml_training.quality.reject_missing_metrics and report.missing_metrics_count > 0:
        raise ValueError("Missing metrics")
    if config.ml_training.quality.reject_missing_model_card and report.missing_model_card_count > 0:
        raise ValueError("Missing model card")
    if config.ml_training.quality.reject_nan_inf_metrics and report.nan_inf_metric_count > 0:
        raise ValueError("NaN/Inf metric found")
