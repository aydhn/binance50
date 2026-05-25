import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindow


def slice_window_data(
    df: pd.DataFrame, window: WalkForwardWindow
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_df = df.iloc[window.train_start : window.train_end].copy()
    val_df = df.iloc[window.validation_start : window.validation_end].copy()
    test_df = df.iloc[window.test_start : window.test_end].copy()
    return train_df, val_df, test_df


def apply_embargo_and_gaps(
    df: pd.DataFrame, window: WalkForwardWindow, config: AppConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    wf_config = config.walkforward

    val_start = (
        window.validation_start
        + wf_config.windows.gap_bars_between_train_validation
        + window.embargo_bars
    )
    val_df = df.iloc[val_start : window.validation_end].copy()

    test_start = (
        window.test_start + wf_config.windows.gap_bars_between_validation_test + window.embargo_bars
    )
    test_df = df.iloc[test_start : window.test_end].copy()

    train_df = df.iloc[window.train_start : window.train_end].copy()
    return train_df, val_df, test_df


def validate_window_splits(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
    window: WalkForwardWindow,
    config: AppConfig,
) -> None:
    if len(train_df) < config.walkforward.windows.min_train_bars:
        raise ValueError(
            f"Train set has {len(train_df)} rows, minimum is {config.walkforward.windows.min_train_bars}"
        )
    if len(validation_df) < config.walkforward.windows.min_validation_bars:
        raise ValueError(
            f"Validation set has {len(validation_df)} rows, minimum is {config.walkforward.windows.min_validation_bars}"
        )
    if len(test_df) < config.walkforward.windows.min_test_bars:
        raise ValueError(
            f"Test set has {len(test_df)} rows, minimum is {config.walkforward.windows.min_test_bars}"
        )

    assert_no_split_overlap(train_df, validation_df, test_df)


def build_window_split_metadata(
    window: WalkForwardWindow,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> dict:
    def safe_get_time(df: pd.DataFrame, idx: int) -> str:
        if len(df) == 0:
            return ""
        if "open_time" in df.columns:
            return str(df["open_time"].iloc[idx])
        return str(df.index[idx])

    return {
        "train_start_time": safe_get_time(train_df, 0),
        "train_end_time": safe_get_time(train_df, -1),
        "validation_start_time": safe_get_time(validation_df, 0),
        "validation_end_time": safe_get_time(validation_df, -1),
        "test_start_time": safe_get_time(test_df, 0),
        "test_end_time": safe_get_time(test_df, -1),
        "train_rows": len(train_df),
        "validation_rows": len(validation_df),
        "test_rows": len(test_df),
    }


def assert_no_split_overlap(
    train_df: pd.DataFrame, validation_df: pd.DataFrame, test_df: pd.DataFrame
) -> None:
    if not train_df.empty and not validation_df.empty:
        if "open_time" in train_df.columns and "open_time" in validation_df.columns:
            assert train_df["open_time"].max() < validation_df["open_time"].min(), (
                "Train and Validation sets overlap"
            )
        else:
            assert train_df.index.max() < validation_df.index.min(), (
                "Train and Validation sets overlap"
            )

    if not validation_df.empty and not test_df.empty:
        if "open_time" in validation_df.columns and "open_time" in test_df.columns:
            assert validation_df["open_time"].max() < test_df["open_time"].min(), (
                "Validation and Test sets overlap"
            )
        else:
            assert validation_df.index.max() < test_df.index.min(), (
                "Validation and Test sets overlap"
            )
