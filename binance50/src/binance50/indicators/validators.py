import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorInputError, LookaheadBiasError

REQUIRED_COLUMNS = ["open_time", "open", "high", "low", "close", "volume"]

FORBIDDEN_COLUMNS = ["future_return", "target", "label", "next_close", "forward"]


def validate_ohlcv_input(df: pd.DataFrame, config: AppConfig) -> None:
    if df is None or df.empty:
        raise IndicatorInputError("Input dataframe is empty or None")

    validate_required_columns(df, REQUIRED_COLUMNS)

    if config.indicators.enforce_monotonic_time:
        validate_monotonic_open_time(df)

    if config.indicators.reject_duplicate_open_time:
        validate_no_duplicate_open_time(df)

    if config.indicators.prevent_lookahead_bias:
        assert_no_lookahead_columns(df)

    if config.indicators.require_closed_candles:
        validate_closed_candles(df, config)


def validate_required_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise IndicatorInputError(f"Missing required columns: {missing}")

    for col in required:
        if col != "open_time" and not pd.api.types.is_numeric_dtype(df[col]):
            raise IndicatorInputError(f"Column {col} must be numeric")


def validate_monotonic_open_time(df: pd.DataFrame) -> None:
    if not df["open_time"].is_monotonic_increasing:
        raise IndicatorInputError("open_time column is not monotonic ascending")


def validate_no_duplicate_open_time(df: pd.DataFrame) -> None:
    if df["open_time"].duplicated().any():
        raise IndicatorInputError("open_time column contains duplicates")


def validate_closed_candles(df: pd.DataFrame, config: AppConfig) -> None:
    if "is_closed" in df.columns:
        if not df["is_closed"].all():
            if config.indicators.drop_incomplete_last_candle:
                # Engine should handle dropping it. The validator just warns or fails.
                # If we get here and it's not all True, and we don't drop, it's an error.
                if df["is_closed"].iloc[:-1].all() and not df["is_closed"].iloc[-1]:
                    pass  # engine will drop it
                else:
                    raise IndicatorInputError("Found incomplete candles that are not the last row")
            else:
                raise IndicatorInputError(
                    "Dataframe contains unclosed candles but drop_incomplete_last_candle is false"
                )


def validate_indicator_output(df: pd.DataFrame, config: AppConfig) -> None:
    if config.indicators.prevent_lookahead_bias:
        assert_no_lookahead_columns(df)


def validate_indicator_column_names(columns: list[str]) -> None:
    pass


def assert_no_lookahead_columns(df: pd.DataFrame) -> None:
    for col in df.columns:
        col_lower = col.lower()
        if any(forbidden in col_lower for forbidden in FORBIDDEN_COLUMNS):
            raise LookaheadBiasError(f"Forbidden column name detected (Lookahead Bias risk): {col}")
