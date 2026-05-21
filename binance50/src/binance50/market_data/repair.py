from typing import Literal

import pandas as pd

from binance50.config.models import AppConfig
from binance50.market_data.incremental import (
    compute_missing_ranges,
    drop_incomplete_last_candle,
)


def repair_sort_by_open_time(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values(by="open_time").reset_index(drop=True)


def repair_deduplicate_open_time(
    df: pd.DataFrame, keep: Literal["last", "first"] = "last"
) -> pd.DataFrame:
    if df.empty:
        return df
    sorted_df = repair_sort_by_open_time(df)
    return sorted_df.drop_duplicates(subset=["open_time"], keep=keep).reset_index(drop=True)


def repair_drop_incomplete_last_candle(
    df: pd.DataFrame, interval: str, now_ms: int | None, config: AppConfig
) -> pd.DataFrame:
    return drop_incomplete_last_candle(df, interval, now_ms, config)


def repair_basic_ohlcv(df: pd.DataFrame, config: AppConfig) -> tuple[pd.DataFrame, list[str]]:
    """Performs safe, basic repairs like sorting and deduplication."""
    if df.empty:
        return df, []

    actions_taken = []

    # 1. Deduplicate & sort
    original_len = len(df)
    repaired_df = repair_deduplicate_open_time(df, keep="last")
    if len(repaired_df) < original_len:
        actions_taken.append(f"Deduplicated {original_len - len(repaired_df)} rows")

    # Check if sorting was needed (deduplicate already sorts, but we can note it)
    if not df["open_time"].is_monotonic_increasing:
        actions_taken.append("Sorted by open_time")

    return repaired_df, actions_taken


def build_gap_fill_plan(
    df: pd.DataFrame, interval: str, config: AppConfig
) -> list[tuple[int, int]]:
    """Returns ranges that need fetching to fill gaps. Does not fetch."""
    if df.empty:
        return []

    # Needs to be sorted first
    sorted_df = repair_sort_by_open_time(df)
    return compute_missing_ranges(sorted_df, interval)
