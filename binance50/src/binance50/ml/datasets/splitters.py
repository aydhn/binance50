import pandas as pd
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLSplitError
from binance50.ml.datasets.models import MLSplitMetadata, MLLabelSpec


def chronological_ml_split(dataset_df: pd.DataFrame, config: AppConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, MLSplitMetadata]:
    if not config.ml_dataset or not config.ml_dataset.splits.enabled:
        raise MLSplitError("ML splitting is disabled in config")

    if dataset_df.empty:
        raise MLSplitError("Cannot split an empty dataframe")

    splits_config = config.ml_dataset.splits

    total_rows = len(dataset_df)
    train_end_idx = int(total_rows * splits_config.train_pct)
    val_end_idx = train_end_idx + int(total_rows * splits_config.validation_pct)

    train_df = dataset_df.iloc[:train_end_idx]
    validation_df = dataset_df.iloc[train_end_idx:val_end_idx]
    test_df = dataset_df.iloc[val_end_idx:]

    validate_ml_splits(train_df, validation_df, test_df, config)

    metadata = MLSplitMetadata(
        split_id="chronological_1",
        split_method="chronological",
        train_start=train_df["open_time"].min() if not train_df.empty else "",
        train_end=train_df["open_time"].max() if not train_df.empty else "",
        validation_start=validation_df["open_time"].min() if not validation_df.empty else "",
        validation_end=validation_df["open_time"].max() if not validation_df.empty else "",
        test_start=test_df["open_time"].min() if not test_df.empty else "",
        test_end=test_df["open_time"].max() if not test_df.empty else "",
        train_rows=len(train_df),
        validation_rows=len(validation_df),
        test_rows=len(test_df),
        embargo_bars=splits_config.embargo_bars,
        purge_overlapping_labels=splits_config.purge_overlapping_labels
    )

    return train_df, validation_df, test_df, metadata

def build_time_series_cv_metadata(dataset_df: pd.DataFrame, config: AppConfig) -> list[dict[str, Any]]:
    # Skeleton implementation
    if not config.ml_dataset or not config.ml_dataset.splits.time_series_cv_enabled:
        return []
    splits_count = config.ml_dataset.splits.time_series_cv_splits
    return [{"split_index": i} for i in range(splits_count)]

def purge_overlapping_label_rows(train_df: pd.DataFrame, validation_df: pd.DataFrame, test_df: pd.DataFrame, label_specs: list[MLLabelSpec], config: AppConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Skeleton logic: drop last N rows of train based on max label horizon to prevent overlap
    if not config.ml_dataset or not config.ml_dataset.splits.purge_overlapping_labels:
        return train_df, validation_df, test_df

    max_horizon = max((spec.horizon_bars for spec in label_specs), default=0)
    if max_horizon > 0:
        train_df = train_df.iloc[:-max_horizon]
        validation_df = validation_df.iloc[:-max_horizon]
    return train_df, validation_df, test_df

def apply_embargo(dataset_df: pd.DataFrame, split_metadata: MLSplitMetadata, config: AppConfig) -> tuple[pd.DataFrame, MLSplitMetadata]:
    # Skeleton implementation
    return dataset_df, split_metadata

def validate_ml_splits(train_df: pd.DataFrame, validation_df: pd.DataFrame, test_df: pd.DataFrame, config: AppConfig) -> None:
    splits_config = config.ml_dataset.splits

    if len(train_df) < splits_config.min_train_rows:
        raise MLSplitError(f"Train rows {len(train_df)} < min {splits_config.min_train_rows}")

    if len(validation_df) < splits_config.min_validation_rows:
        raise MLSplitError(f"Validation rows {len(validation_df)} < min {splits_config.min_validation_rows}")

    if len(test_df) < splits_config.min_test_rows:
        raise MLSplitError(f"Test rows {len(test_df)} < min {splits_config.min_test_rows}")

    if not train_df.empty and not validation_df.empty:
        if train_df["open_time"].max() >= validation_df["open_time"].min():
            raise MLSplitError("Split overlap detected between train and validation")

    if not validation_df.empty and not test_df.empty:
        if validation_df["open_time"].max() >= test_df["open_time"].min():
            raise MLSplitError("Split overlap detected between validation and test")

def build_ml_split_report(split_metadata: MLSplitMetadata) -> dict[str, Any]:
    return split_metadata.model_dump(mode="json")
