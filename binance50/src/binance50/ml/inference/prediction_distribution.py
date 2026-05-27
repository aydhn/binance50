from typing import Any, Dict, List
import numpy as np
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from collections import Counter

class MLPredictionDistributionReport(BaseModel):
    model_id: str
    dataset_id: str
    split_name: str
    row_count: int
    predicted_class_distribution: Dict[str, float]
    probability_distribution_summary: Dict[str, float]
    confidence_summary: Dict[str, float]
    single_class_ratio: float
    single_class_collapse_warning: bool
    low_confidence_warning: bool
    probability_collapse_warning: bool
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def compute_class_distribution(predictions: List[MLPredictionRow]) -> Dict[str, float]:
    if not predictions:
        return {}
    counts = Counter(p.predicted_label for p in predictions)
    total = len(predictions)
    return {str(k): float(v/total) for k, v in counts.items()}

def compute_probability_distribution_summary(predictions: List[MLPredictionRow]) -> Dict[str, float]:
    probs = [p.max_probability for p in predictions if p.max_probability is not None]
    if not probs:
        return {}
    return {
        "min": float(np.min(probs)),
        "max": float(np.max(probs)),
        "mean": float(np.mean(probs)),
        "std": float(np.std(probs)),
        "q25": float(np.percentile(probs, 25)),
        "q50": float(np.percentile(probs, 50)),
        "q75": float(np.percentile(probs, 75))
    }

def detect_single_class_prediction_collapse(predictions: List[MLPredictionRow], config: AppConfig) -> bool:
    dist = compute_class_distribution(predictions)
    if not dist:
        return False
    max_ratio = max(dist.values())
    return max_ratio >= config.ml_inference.distribution.warn_single_class_prediction_ratio

def detect_low_confidence(predictions: List[MLPredictionRow], config: AppConfig) -> bool:
    summary = compute_probability_distribution_summary(predictions)
    if not summary:
        return False
    return summary.get("mean", 1.0) < config.ml_inference.distribution.warn_low_confidence_mean

def detect_probability_collapse(predictions: List[MLPredictionRow], config: AppConfig) -> bool:
    summary = compute_probability_distribution_summary(predictions)
    if not summary:
        return False
    return summary.get("std", 1.0) < 0.01  # Arbitrary small std for collapse

def analyze_prediction_distribution(predictions: List[MLPredictionRow], config: AppConfig) -> MLPredictionDistributionReport:
    dist = compute_class_distribution(predictions)
    max_ratio = max(dist.values()) if dist else 0.0

    single_collapse = detect_single_class_prediction_collapse(predictions, config)
    low_conf = detect_low_confidence(predictions, config)
    prob_collapse = detect_probability_collapse(predictions, config)

    warnings = []
    if single_collapse: warnings.append("Single class prediction collapse detected")
    if low_conf: warnings.append("Low overall confidence mean")
    if prob_collapse: warnings.append("Probability distribution collapsed (very low variance)")

    return MLPredictionDistributionReport(
        model_id="unknown",
        dataset_id="unknown",
        split_name="unknown",
        row_count=len(predictions),
        predicted_class_distribution=dist,
        probability_distribution_summary=compute_probability_distribution_summary(predictions),
        confidence_summary=compute_probability_distribution_summary(predictions), # simplifying
        single_class_ratio=max_ratio,
        single_class_collapse_warning=single_collapse,
        low_confidence_warning=low_conf,
        probability_collapse_warning=prob_collapse,
        warnings=warnings
    )
