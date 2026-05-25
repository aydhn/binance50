import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig


class DataSplitMetadata(BaseModel):
    train_start: int | None = None
    train_end: int | None = None
    validation_start: int | None = None
    validation_end: int | None = None
    test_start: int | None = None
    test_end: int | None = None
    train_rows: int = 0
    validation_rows: int = 0
    test_rows: int = 0
    embargo_bars: int = 0
    method: str = "chronological"
    warnings: list[str] = Field(default_factory=list)


def chronological_train_validation_test_split(
    df: pd.DataFrame, config: AppConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, DataSplitMetadata]:
    if len(df) == 0:
        raise ValueError("Cannot split empty dataframe")

    total_rows = len(df)
    train_pct = config.optimizer.data_split.train_pct
    val_pct = config.optimizer.data_split.validation_pct
    embargo = config.optimizer.data_split.embargo_bars

    train_size = int(total_rows * train_pct)
    val_size = int(total_rows * val_pct)

    # Adjust for embargo
    train_end_idx = train_size
    val_start_idx = train_end_idx + embargo
    val_end_idx = val_start_idx + val_size
    test_start_idx = val_end_idx + embargo

    train_df = df.iloc[:train_end_idx]
    val_df = df.iloc[val_start_idx:val_end_idx]
    test_df = df.iloc[test_start_idx:]

    metadata = DataSplitMetadata(
        train_start=int(train_df.index[0]) if not train_df.empty else None,
        train_end=int(train_df.index[-1]) if not train_df.empty else None,
        validation_start=int(val_df.index[0]) if not val_df.empty else None,
        validation_end=int(val_df.index[-1]) if not val_df.empty else None,
        test_start=int(test_df.index[0]) if not test_df.empty else None,
        test_end=int(test_df.index[-1]) if not test_df.empty else None,
        train_rows=len(train_df),
        validation_rows=len(val_df),
        test_rows=len(test_df),
        embargo_bars=embargo,
        method="chronological",
    )

    validate_split_min_rows(metadata, config)
    validate_split_no_overlap(metadata)

    return train_df, val_df, test_df, metadata


def build_time_series_cv_splits(df: pd.DataFrame, config: AppConfig) -> list[dict]:
    if not config.optimizer.data_split.time_series_cv_enabled:
        return []

    splits = config.optimizer.data_split.time_series_cv_splits
    if splits <= 1:
        return []

    total_rows = len(df)
    test_size = total_rows // (splits + 1)

    cv_splits = []
    for i in range(splits):
        train_end = (i + 1) * test_size
        test_end = train_end + test_size

        # apply embargo
        embargo = config.optimizer.data_split.embargo_bars
        actual_test_start = train_end + embargo

        cv_splits.append(
            {
                "split_id": i,
                "train_start_idx": 0,
                "train_end_idx": train_end,
                "test_start_idx": actual_test_start,
                "test_end_idx": test_end,
            }
        )

    return cv_splits


def validate_split_no_overlap(metadata: DataSplitMetadata) -> None:
    # Ensure strict time ordering: train < validation < test
    if metadata.train_end and metadata.validation_start:
        if metadata.train_end >= metadata.validation_start:
            raise ValueError("Overlap detected between train and validation splits")

    if metadata.validation_end and metadata.test_start:
        if metadata.validation_end >= metadata.test_start:
            raise ValueError("Overlap detected between validation and test splits")


def validate_split_min_rows(metadata: DataSplitMetadata, config: AppConfig) -> None:
    if metadata.train_rows < config.optimizer.data_split.min_train_rows:
        raise ValueError(
            f"Train rows ({metadata.train_rows}) below minimum ({config.optimizer.data_split.min_train_rows})"
        )

    if metadata.validation_rows < config.optimizer.data_split.min_validation_rows:
        raise ValueError(
            f"Validation rows ({metadata.validation_rows}) below minimum ({config.optimizer.data_split.min_validation_rows})"
        )

    if metadata.test_rows < config.optimizer.data_split.min_test_rows:
        raise ValueError(
            f"Test rows ({metadata.test_rows}) below minimum ({config.optimizer.data_split.min_test_rows})"
        )


def apply_embargo_between_splits(
    df: pd.DataFrame, metadata: DataSplitMetadata, config: AppConfig
) -> tuple:
    # Logic is implemented within chronological split for simplicity here
    pass


def build_split_report(metadata: DataSplitMetadata) -> dict:
    return metadata.model_dump()
