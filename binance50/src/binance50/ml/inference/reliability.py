from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow

def compute_bin_count(bin_predictions: List[MLPredictionRow]) -> int:
    return len(bin_predictions)

def compute_bin_confidence(bin_predictions: List[MLPredictionRow]) -> Optional[float]:
    if not bin_predictions:
        return None
    probs = [p.max_probability for p in bin_predictions if p.max_probability is not None]
    if not probs:
        return None
    return float(np.mean(probs))

def compute_bin_accuracy(bin_predictions: List[MLPredictionRow], labels: pd.Series) -> Optional[float]:
    if not bin_predictions or labels is None or len(labels) != len(bin_predictions):
        return None

    correct = 0
    # Assuming labels correspond 1:1 by index for simplicity in this dummy
    for i, p in enumerate(bin_predictions):
        if str(labels.iloc[i]) == p.predicted_label:
            correct += 1

    return float(correct) / len(bin_predictions)

def build_reliability_bins(predictions: List[MLPredictionRow], labels: Optional[pd.Series], bins: int, config: AppConfig) -> List[Dict[str, Any]]:
    # Simple uniform binning [0, 1]
    bin_edges = np.linspace(0, 1, bins + 1)

    result_bins = []

    for i in range(bins):
        start = bin_edges[i]
        end = bin_edges[i+1]

        # In a real implementation we need to correctly align labels with sorted/filtered predictions
        # For simplicity we assume predictions and labels indices align
        bin_preds = []
        bin_labels_list = []

        for j, p in enumerate(predictions):
            prob = p.max_probability
            if prob is not None:
                if (start <= prob <= end) if i == bins - 1 else (start <= prob < end):
                    bin_preds.append(p)
                    if labels is not None:
                        bin_labels_list.append(labels.iloc[j])

        bin_labels_series = pd.Series(bin_labels_list) if bin_labels_list else None

        result_bins.append({
            "bin_start": float(start),
            "bin_end": float(end),
            "count": compute_bin_count(bin_preds),
            "confidence": compute_bin_confidence(bin_preds),
            "accuracy": compute_bin_accuracy(bin_preds, bin_labels_series)
        })

    return result_bins

def reliability_bins_to_dataframe(bins: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(bins)

def validate_reliability_bins(bins: List[Dict[str, Any]], config: AppConfig) -> None:
    pass
