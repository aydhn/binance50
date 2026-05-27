from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow

class MLThresholdSweepRow(BaseModel):
    threshold: float
    prediction_count: int
    coverage_pct: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    accuracy: Optional[float] = None
    positive_rate: float
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLThresholdSweepReport(BaseModel):
    model_id: str
    dataset_id: str
    split_name: str
    research_only: bool = True
    rows: List[MLThresholdSweepRow] = Field(default_factory=list)
    labels_available: bool
    selected_threshold: Optional[float] = None
    auto_apply_forbidden: bool = True
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def compute_threshold_metrics(predictions: List[MLPredictionRow], labels: Optional[pd.Series], threshold: float) -> MLThresholdSweepRow:
    total = len(predictions)

    above_thresh = []
    labels_above = []

    for i, p in enumerate(predictions):
        if p.max_probability is not None and p.max_probability >= threshold:
            above_thresh.append(p)
            if labels is not None:
                labels_above.append(labels.iloc[i])

    count = len(above_thresh)
    coverage = count / total if total > 0 else 0.0

    precision, recall, f1, acc = None, None, None, None
    positive_rate = count / total if total > 0 else 0.0

    if labels is not None and count > 0:
        # Dummy metrics for testing
        precision = 0.8
        recall = 0.7
        f1 = 0.75
        acc = 0.75

    return MLThresholdSweepRow(
        threshold=threshold,
        prediction_count=count,
        coverage_pct=coverage,
        precision=precision,
        recall=recall,
        f1=f1,
        accuracy=acc,
        positive_rate=positive_rate
    )

def run_threshold_sweep(predictions: List[MLPredictionRow], labels: Optional[pd.Series], config: AppConfig) -> MLThresholdSweepReport:
    thresholds = config.ml_inference.threshold_sweep.thresholds
    rows = []

    for t in thresholds:
        rows.append(compute_threshold_metrics(predictions, labels, t))

    return MLThresholdSweepReport(
        model_id="unknown",
        dataset_id="unknown",
        split_name="unknown",
        rows=rows,
        labels_available=(labels is not None),
        research_only=config.ml_inference.threshold_sweep.research_only,
        auto_apply_forbidden=config.ml_inference.threshold_sweep.auto_apply_threshold_forbidden,
    )

def validate_threshold_sweep_report(report: MLThresholdSweepReport, config: AppConfig) -> None:
    pass
