from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import InsufficientHistoryError
from binance50.indicators.models import IndicatorSpec


def estimate_indicator_lookback(spec: IndicatorSpec) -> int:
    return spec.min_lookback


def estimate_max_lookback(specs: list[IndicatorSpec]) -> int:
    if not specs:
        return 0
    return max(spec.min_lookback for spec in specs)


def mark_warmup_rows(df: pd.DataFrame, max_lookback: int) -> pd.DataFrame:
    df = df.copy()
    warmup_mask = [True] * min(max_lookback, len(df)) + [False] * max(0, len(df) - max_lookback)
    df["is_warmup"] = warmup_mask
    return df


def compute_valid_row_mask(
    df: pd.DataFrame, indicator_columns: list[str], min_valid_ratio: float
) -> pd.Series:
    if not indicator_columns:
        return pd.Series([True] * len(df), index=df.index)

    valid_mask = df[indicator_columns].notna().all(axis=1)

    valid_ratio = valid_mask.sum() / len(df) if len(df) > 0 else 0
    if valid_ratio < min_valid_ratio:
        # We might want to handle this differently later, but returning the mask
        pass

    return valid_mask


def summarize_warmup(
    df: pd.DataFrame, indicator_columns: list[str], max_lookback: int
) -> dict[str, Any]:
    warmup_rows = min(max_lookback, len(df))
    valid_rows = len(df) - warmup_rows

    first_valid_times = {}
    if "open_time" in df.columns:
        for col in indicator_columns:
            if col in df.columns:
                valid_idx = df[col].first_valid_index()
                if valid_idx is not None:
                    first_valid_times[col] = df.loc[valid_idx, "open_time"]

    return {
        "max_lookback": max_lookback,
        "warmup_rows": warmup_rows,
        "valid_rows": valid_rows,
        "first_valid_times": first_valid_times,
    }


def assert_sufficient_history(
    df: pd.DataFrame, specs: list[IndicatorSpec], config: AppConfig
) -> None:
    min_required = config.indicators.min_rows_required
    max_lookback = estimate_max_lookback(specs)

    if len(df) < min_required:
        raise InsufficientHistoryError(
            f"Insufficient history: {len(df)} rows, minimum required is {min_required}"
        )

    if len(df) <= max_lookback:
        raise InsufficientHistoryError(
            f"Insufficient history: {len(df)} rows, max lookback is {max_lookback}"
        )
