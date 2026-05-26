import pandas as pd
from typing import Any, Dict, List
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLTaskType

def extract_target(dataset_result: Any, label_column: str, split_name: str) -> pd.Series:
    return pd.Series([0, 1])

def detect_single_class(y: pd.Series) -> bool:
    return len(y.unique()) <= 1

def detect_class_imbalance(y: pd.Series, config: AppConfig) -> Dict[str, Any]:
    counts = y.value_counts(normalize=True)
    imbalanced = counts.max() > config.ml_dataset.quality.max_majority_class_ratio
    return {"imbalanced": imbalanced, "max_ratio": float(counts.max())}

def validate_target(y: pd.Series, task_type: MLTaskType, config: AppConfig) -> None:
    if task_type == MLTaskType.classification:
        if detect_single_class(y) and config.ml_training.quality.reject_single_class_train:
            raise ValueError("Single class found in target")

def infer_class_labels(y: pd.Series) -> List[Any]:
    return sorted(y.unique().tolist())

def build_class_weight_report(y_train: pd.Series) -> Dict[str, Any]:
    counts = y_train.value_counts().to_dict()
    total = len(y_train)
    weights = {k: total / (len(counts) * v) for k, v in counts.items()}
    return {"counts": counts, "weights": weights}
