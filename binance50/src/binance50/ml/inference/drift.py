from typing import Any, Dict, List
import pandas as pd
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.core.exceptions import MLInferenceDriftError

class MLInferenceDriftReport(BaseModel):
    model_id: str
    dataset_id: str
    compare_to_training_feature_stats: bool
    feature_shift_summary: Dict[str, Any]
    prediction_shift_summary: Dict[str, Any]
    psi_skeleton: Dict[str, Any]
    high_feature_shift_warning: bool
    high_prediction_shift_warning: bool
    skeleton_only: bool = True
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def compute_basic_feature_shift(current_features: pd.DataFrame, training_feature_stats: Dict[str, Any]) -> Dict[str, Any]:
    # Dummy mock
    if not training_feature_stats:
        return {}
    return {"shift_detected": False, "score": 0.05}

def compute_prediction_shift(predictions: List[MLPredictionRow], training_prediction_reference: Dict[str, Any]) -> Dict[str, Any]:
    # Dummy mock
    if not training_prediction_reference:
        return {}
    return {"shift_detected": False, "score": 0.02}

def compute_psi_skeleton(current: pd.Series, reference: pd.Series, bins: int = 10) -> Dict[str, Any]:
    # Dummy mock
    return {"psi_score": 0.0}

def build_inference_drift_report(current_features: pd.DataFrame, predictions: List[MLPredictionRow], model_result: Any, config: AppConfig) -> MLInferenceDriftReport:
    # Dummy references
    training_f_stats = getattr(model_result, "feature_stats", {})
    training_p_stats = getattr(model_result, "prediction_stats", {})

    f_shift = {}
    p_shift = {}
    psi = {}

    high_f_shift = False
    high_p_shift = False
    warnings = []

    if config.ml_inference.drift.compare_to_training_feature_stats:
        if config.ml_inference.drift.compute_basic_feature_shift:
            f_shift = compute_basic_feature_shift(current_features, training_f_stats)
            if f_shift.get("score", 0) > config.ml_inference.drift.drift_threshold_warning:
                high_f_shift = True
                warnings.append("High feature shift detected")

        if config.ml_inference.drift.compute_prediction_shift:
            p_shift = compute_prediction_shift(predictions, training_p_stats)
            if p_shift.get("score", 0) > config.ml_inference.drift.drift_threshold_warning:
                high_p_shift = True
                warnings.append("High prediction shift detected")

        if config.ml_inference.drift.compute_population_stability_index_skeleton:
            # Mock series
            psi = compute_psi_skeleton(pd.Series([1]), pd.Series([1]), bins=10)

    return MLInferenceDriftReport(
        model_id=getattr(model_result, "run_id", "unknown"),
        dataset_id="unknown",
        compare_to_training_feature_stats=config.ml_inference.drift.compare_to_training_feature_stats,
        feature_shift_summary=f_shift,
        prediction_shift_summary=p_shift,
        psi_skeleton=psi,
        high_feature_shift_warning=high_f_shift,
        high_prediction_shift_warning=high_p_shift,
        skeleton_only=config.ml_inference.drift.skeleton_only,
        warnings=warnings
    )

def validate_drift_report(report: MLInferenceDriftReport, config: AppConfig) -> None:
    pass
