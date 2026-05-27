from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.core.exceptions import MLProbabilityError

class MLProbabilityReport(BaseModel):
    model_id: str
    probability_available: bool
    calibrated: Optional[bool] = None
    calibration_method: Optional[str] = None
    row_count: int
    probability_min: Optional[float] = None
    probability_max: Optional[float] = None
    probability_mean: Optional[float] = None
    probability_sum_invalid_count: int
    out_of_range_count: int
    uncalibrated_warning: bool
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def check_probability_sum(prediction: MLPredictionRow, tolerance: float) -> bool:
    if not prediction.probabilities:
        return True
    return abs(sum(prediction.probabilities.values()) - 1.0) <= tolerance

def compute_max_probability(prediction: MLPredictionRow) -> Optional[float]:
    if not prediction.probabilities:
        return None
    return max(prediction.probabilities.values())

def validate_probability_outputs(predictions: List[MLPredictionRow], config: AppConfig) -> None:
    min_p = config.ml_inference.probability.min_probability
    max_p = config.ml_inference.probability.max_probability
    tolerance = config.ml_inference.probability.probability_sum_tolerance

    for p in predictions:
        if not p.probabilities:
            continue

        for val in p.probabilities.values():
            if val < min_p or val > max_p:
                if config.ml_inference.probability.reject_probability_out_of_range:
                    raise MLProbabilityError(f"Probability out of range: {val}")

        if config.ml_inference.probability.reject_probability_sum_invalid:
            if not check_probability_sum(p, tolerance):
                raise MLProbabilityError(f"Probability sum invalid for {p.prediction_id}")

def mark_uncalibrated_if_needed(predictions: List[MLPredictionRow], model_result: Any) -> List[MLPredictionRow]:
    calibrated = getattr(model_result, "calibrated", False)
    cal_method = getattr(model_result, "calibration_method", "unknown")

    for p in predictions:
        p.calibrated = calibrated
        p.calibration_method = cal_method if calibrated else None

    return predictions

def compute_probability_report(predictions: List[MLPredictionRow], model_result: Any, config: AppConfig) -> MLProbabilityReport:
    has_prob = any(p.probabilities is not None for p in predictions)

    if not has_prob:
        return MLProbabilityReport(
            model_id=getattr(model_result, "run_id", "unknown"),
            probability_available=False,
            row_count=len(predictions),
            probability_sum_invalid_count=0,
            out_of_range_count=0,
            uncalibrated_warning=False
        )

    all_probs = []
    invalid_sum = 0
    out_of_range = 0
    tolerance = config.ml_inference.probability.probability_sum_tolerance

    for p in predictions:
        if p.probabilities:
            all_probs.extend(p.probabilities.values())
            if not check_probability_sum(p, tolerance):
                invalid_sum += 1
            for v in p.probabilities.values():
                if v < 0.0 or v > 1.0:
                    out_of_range += 1

    calibrated = getattr(model_result, "calibrated", False)
    warnings = []

    if not calibrated and config.ml_inference.probability.warn_uncalibrated_probability:
        warnings.append("Uncalibrated probability detected")

    return MLProbabilityReport(
        model_id=getattr(model_result, "run_id", "unknown"),
        probability_available=True,
        calibrated=calibrated,
        calibration_method=getattr(model_result, "calibration_method", "unknown") if calibrated else None,
        row_count=len(predictions),
        probability_min=min(all_probs) if all_probs else None,
        probability_max=max(all_probs) if all_probs else None,
        probability_mean=sum(all_probs)/len(all_probs) if all_probs else None,
        probability_sum_invalid_count=invalid_sum,
        out_of_range_count=out_of_range,
        uncalibrated_warning=(not calibrated),
        warnings=warnings
    )
