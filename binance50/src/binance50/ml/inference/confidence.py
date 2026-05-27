from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow

class MLConfidenceBucketReport(BaseModel):
    bucket_start: float
    bucket_end: float
    count: int
    ratio: float
    accuracy_if_labels_available: Optional[float] = None
    avg_confidence: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def compute_confidence_for_prediction(prediction: MLPredictionRow) -> Optional[float]:
    return prediction.max_probability

def build_confidence_buckets(predictions: List[MLPredictionRow], labels: Optional[pd.Series], config: AppConfig) -> List[MLConfidenceBucketReport]:
    buckets_cfg = config.ml_inference.distribution.confidence_buckets
    total = len(predictions)

    reports = []
    for bucket in buckets_cfg:
        start, end = bucket[0], bucket[1]

        b_preds = []
        b_labels = []
        for i, p in enumerate(predictions):
            conf = compute_confidence_for_prediction(p)
            if conf is not None:
                # end bucket inclusive if 1.0
                if start <= conf <= end if end == 1.0 else start <= conf < end:
                    b_preds.append(p)
                    if labels is not None:
                        b_labels.append(labels.iloc[i])

        count = len(b_preds)
        ratio = count / total if total > 0 else 0.0
        avg_conf = float(np.mean([p.max_probability for p in b_preds])) if b_preds else None

        acc = None
        if labels is not None and count > 0:
            correct = sum(1 for i, p in enumerate(b_preds) if p.predicted_label == str(b_labels[i]))
            acc = correct / count

        reports.append(MLConfidenceBucketReport(
            bucket_start=start,
            bucket_end=end,
            count=count,
            ratio=ratio,
            accuracy_if_labels_available=acc,
            avg_confidence=avg_conf
        ))

    return reports

def confidence_buckets_to_dataframe(buckets: List[MLConfidenceBucketReport]) -> pd.DataFrame:
    return pd.DataFrame([b.model_dump() for b in buckets])

def summarize_confidence_buckets(buckets: List[MLConfidenceBucketReport]) -> Dict[str, Any]:
    return {
        "total_buckets": len(buckets),
        "highest_density_bucket": max(buckets, key=lambda b: b.count).bucket_start if buckets else None
    }
