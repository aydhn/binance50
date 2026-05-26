import numpy as np
import pandas as pd
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLLabelError
from binance50.ml.datasets.models import MLLabelSpec, MLLabelType


def build_labels(df: pd.DataFrame, specs: list[MLLabelSpec], config: AppConfig) -> pd.DataFrame:
    labels_df = pd.DataFrame(index=df.index)

    for spec in specs:
        if spec.label_type == MLLabelType.FORWARD_RETURN_REGRESSION:
             labels_df[spec.label_column], labels_df[spec.future_return_column] = compute_forward_return_label(df, spec)
        elif spec.label_type == MLLabelType.FORWARD_RETURN_CLASSIFICATION:
             labels_df[spec.label_column], labels_df[spec.future_return_column] = compute_forward_return_classification_label(df, spec)
        elif spec.label_type == MLLabelType.VOLATILITY_ADJUSTED_RETURN_CLASSIFICATION:
             labels_df[spec.label_column], labels_df[spec.future_return_column] = compute_volatility_adjusted_label(df, spec, config)
        elif spec.label_type == MLLabelType.TRIPLE_BARRIER_SKELETON:
             labels_df[spec.label_column], labels_df[spec.future_return_column] = build_triple_barrier_skeleton_labels(df, spec, config)
        elif spec.label_type == MLLabelType.RANKING_SKELETON:
             labels_df[spec.label_column], labels_df[spec.future_return_column] = build_ranking_skeleton_labels(df, spec, config)
        else:
            raise MLLabelError(f"Unsupported label type: {spec.label_type}")

    return labels_df

def compute_forward_return_label(df: pd.DataFrame, spec: MLLabelSpec) -> tuple[pd.Series, pd.Series]:
    if spec.return_source not in df.columns:
        raise MLLabelError(f"Return source {spec.return_source} not found")

    src = df[spec.return_source]
    future_return = src.shift(-spec.horizon_bars) / src - 1
    return future_return, future_return

def compute_forward_return_classification_label(df: pd.DataFrame, spec: MLLabelSpec) -> tuple[pd.Series, pd.Series]:
    future_return, _ = compute_forward_return_label(df, spec)

    conditions = [
        future_return > spec.threshold_pct,
        future_return < -spec.threshold_pct
    ]
    choices = [1, -1]

    label_values = np.select(conditions, choices, default=0 if spec.include_neutral_class else np.nan)
    return pd.Series(label_values, index=df.index), future_return

def compute_volatility_adjusted_label(df: pd.DataFrame, spec: MLLabelSpec, config: AppConfig) -> tuple[pd.Series, pd.Series]:
    # Skeleton
    return compute_forward_return_classification_label(df, spec)

def build_triple_barrier_skeleton_labels(df: pd.DataFrame, spec: MLLabelSpec, config: AppConfig) -> tuple[pd.Series, pd.Series]:
    # Skeleton
    return compute_forward_return_classification_label(df, spec)

def build_ranking_skeleton_labels(df: pd.DataFrame, spec: MLLabelSpec, config: AppConfig) -> tuple[pd.Series, pd.Series]:
    # Skeleton
    return compute_forward_return_classification_label(df, spec)

def drop_unlabeled_tail_rows(dataset_df: pd.DataFrame, specs: list[MLLabelSpec], config: AppConfig) -> pd.DataFrame:
    if not config.ml_dataset or not config.ml_dataset.labels.drop_last_horizon_rows:
        return dataset_df

    max_horizon = max((spec.horizon_bars for spec in specs), default=0)
    if max_horizon > 0:
        return dataset_df.iloc[:-max_horizon]
    return dataset_df

def validate_labels(labels_df: pd.DataFrame, config: AppConfig) -> None:
    if labels_df.empty:
        raise MLLabelError("Label DataFrame is empty")
