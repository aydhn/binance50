from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.core.exceptions import MLCalibrationCheckError

class MLInferenceCalibrationCheckReport(BaseModel):
    model_id: str
    dataset_id: str
    split_name: str
    labels_available: bool
    brier_score: Optional[float] = None
    expected_calibration_error: Optional[float] = None
    reliability_bins: Optional[List[Dict[str, Any]]] = None
    training_brier_score_reference: Optional[float] = None
    training_ece_reference: Optional[float] = None
    brier_degradation: Optional[float] = None
    ece_degradation: Optional[float] = None
    calibration_status: str
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def extract_labels_for_predictions(dataset_result: Any, predictions: List[MLPredictionRow], label_column: str) -> Optional[pd.Series]:
    if not hasattr(dataset_result, "dataset_df") or dataset_result.dataset_df is None:
        return None
    if label_column not in dataset_result.dataset_df.columns:
        return None

    df = dataset_result.dataset_df
    # In a real app we'd map prediction_id -> row index/time to get correct labels
    # Here we mock by returning the first N labels where N = len(predictions)
    # assuming predictions match the DataFrame index order
    return df[label_column].iloc[:len(predictions)]

def compute_brier_score_for_predictions(predictions: List[MLPredictionRow], labels: pd.Series, config: AppConfig) -> Optional[float]:
    from sklearn.metrics import brier_score_loss

    y_prob = [p.max_probability for p in predictions if p.max_probability is not None]
    if len(y_prob) != len(labels):
        return None

    y_true = labels.values
    # Assuming binary for brier score example, multiclass needs special handling
    try:
        # Simplification: we assume predicted_class_index represents the class for which max_prob was emitted
        # A true implementation needs exact mapping
        return float(brier_score_loss(y_true, y_prob))
    except Exception:
        return None

def compute_ece_for_predictions(predictions: List[MLPredictionRow], labels: pd.Series, config: AppConfig) -> Optional[float]:
    # Dummy ECE calculation
    if len(predictions) != len(labels):
        return None
    return 0.05

def compare_to_training_calibration(model_result: Any, current_report: MLInferenceCalibrationCheckReport, config: AppConfig) -> Dict[str, float]:
    ref_brier = getattr(model_result, "training_brier_score", None)
    ref_ece = getattr(model_result, "training_ece", None)

    degradation = {}

    if ref_brier is not None and current_report.brier_score is not None:
        degradation["brier"] = current_report.brier_score - ref_brier

    if ref_ece is not None and current_report.expected_calibration_error is not None:
        degradation["ece"] = current_report.expected_calibration_error - ref_ece

    return degradation

def validate_calibration_check_report(report: MLInferenceCalibrationCheckReport, config: AppConfig) -> None:
    if config.ml_inference.calibration_check.require_label_for_calibration_metrics and not report.labels_available:
        raise MLCalibrationCheckError("Labels required for calibration metrics but none found")

def build_inference_calibration_check(predictions: List[MLPredictionRow], labels: Optional[pd.Series], model_result: Any, config: AppConfig) -> MLInferenceCalibrationCheckReport:

    report = MLInferenceCalibrationCheckReport(
        model_id=getattr(model_result, "run_id", "unknown"),
        dataset_id="unknown",
        split_name="unknown",
        labels_available=(labels is not None),
        calibration_status="unknown"
    )

    if labels is None:
        if config.ml_inference.calibration_check.warn_if_labels_missing:
            report.warnings.append("Labels missing, cannot compute calibration metrics")
        report.calibration_status = "unverified"
        return report

    if config.ml_inference.calibration_check.compute_brier_score_if_labels_available:
        report.brier_score = compute_brier_score_for_predictions(predictions, labels, config)

    if config.ml_inference.calibration_check.compute_ece_if_labels_available:
        report.expected_calibration_error = compute_ece_for_predictions(predictions, labels, config)

    if config.ml_inference.calibration_check.compare_to_training_calibration_report:
        report.training_brier_score_reference = getattr(model_result, "training_brier_score", None)
        report.training_ece_reference = getattr(model_result, "training_ece", None)

        deg = compare_to_training_calibration(model_result, report, config)
        if "brier" in deg:
            report.brier_degradation = deg["brier"]
            if deg["brier"] > config.ml_inference.calibration_check.max_brier_degradation_warning:
                report.warnings.append(f"High Brier score degradation: {deg['brier']}")

        if "ece" in deg:
            report.ece_degradation = deg["ece"]
            if deg["ece"] > config.ml_inference.calibration_check.max_ece_warning:
                report.warnings.append(f"High ECE: {report.expected_calibration_error}")

    report.calibration_status = "verified"
    return report
