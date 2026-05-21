import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.market_data.intervals import (
    interval_to_milliseconds,
    is_candle_closed,
)


class IncrementalUpdatePlan(BaseModel):
    symbol: str
    market_scope: MarketScope
    interval: str
    existing_start_open_time: int | None
    existing_end_open_time: int | None
    last_complete_open_time: int | None
    next_start_time_ms: int
    requested_end_time_ms: int
    overlap_candles: int
    needs_update: bool
    reason: str
    warnings: list[str] = Field(default_factory=list)


def find_last_complete_candle(
    df: pd.DataFrame, interval: str, now_ms: int | None = None
) -> int | None:
    if df.empty:
        return None

    sorted_df = df.sort_values(by="open_time", ascending=False)
    for _, row in sorted_df.iterrows():
        open_time = int(row["open_time"])
        close_time = int(row["close_time"])
        if is_candle_closed(open_time, close_time, interval, now_ms):
            return open_time

    return None


def build_incremental_update_plan(
    existing_df: pd.DataFrame | None,
    symbol: str,
    market_scope: MarketScope,
    interval: str,
    requested_end_ms: int,
    config: AppConfig,
    now_ms: int | None = None,
) -> IncrementalUpdatePlan:
    if existing_df is None or existing_df.empty:
        from binance50.market_data.intervals import get_default_history_start

        try:
            start_ms = get_default_history_start(requested_end_ms, interval, config)
        except Exception:
            # Fallback if unsupported or config lacks default history
            ms_per_candle = interval_to_milliseconds(interval)
            start_ms = requested_end_ms - (ms_per_candle * 1000)

        return IncrementalUpdatePlan(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            existing_start_open_time=None,
            existing_end_open_time=None,
            last_complete_open_time=None,
            next_start_time_ms=start_ms,
            requested_end_time_ms=requested_end_ms,
            overlap_candles=0,
            needs_update=True,
            reason="full_fetch_required",
            warnings=[],
        )

    last_complete = find_last_complete_candle(existing_df, interval, now_ms)
    existing_start = int(existing_df["open_time"].min())
    existing_end = int(existing_df["open_time"].max())

    ms_per_candle = interval_to_milliseconds(interval)
    overlap = config.market_data.overlap_candles_on_update

    if last_complete is None:
        # All existing candles are incomplete (rare)
        next_start = existing_start - (overlap * ms_per_candle)
    else:
        next_start = (
            last_complete - ((overlap - 1) * ms_per_candle)
            if overlap > 0
            else last_complete + ms_per_candle
        )

    needs_update = next_start < requested_end_ms

    return IncrementalUpdatePlan(
        symbol=symbol,
        market_scope=market_scope,
        interval=interval,
        existing_start_open_time=existing_start,
        existing_end_open_time=existing_end,
        last_complete_open_time=last_complete,
        next_start_time_ms=next_start,
        requested_end_time_ms=requested_end_ms,
        overlap_candles=overlap,
        needs_update=needs_update,
        reason="incremental_update" if needs_update else "up_to_date",
        warnings=[],
    )


def merge_existing_and_new_ohlcv(
    existing_df: pd.DataFrame | None, new_df: pd.DataFrame, config: AppConfig
) -> pd.DataFrame:
    if existing_df is None or existing_df.empty:
        return deduplicate_by_open_time(new_df)
    if new_df.empty:
        return existing_df

    combined = pd.concat([existing_df, new_df], ignore_index=True)
    return deduplicate_by_open_time(combined)


def deduplicate_by_open_time(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # Keep the last observed row for a given open_time
    sorted_df = df.sort_values(by="open_time")
    deduped = sorted_df.drop_duplicates(subset=["open_time"], keep="last")
    return deduped.reset_index(drop=True)


def drop_incomplete_last_candle(
    df: pd.DataFrame, interval: str, now_ms: int | None, config: AppConfig
) -> pd.DataFrame:
    if df.empty:
        return df

    if not config.market_data.exclude_incomplete_last_candle:
        return df

    sorted_df = df.sort_values(by="open_time").reset_index(drop=True)
    last_row = sorted_df.iloc[-1]

    if not is_candle_closed(
        int(last_row["open_time"]), int(last_row["close_time"]), interval, now_ms
    ):
        return sorted_df.iloc[:-1].reset_index(drop=True)

    return sorted_df


def compute_missing_ranges(df: pd.DataFrame, interval: str) -> list[tuple[int, int]]:
    if df.empty:
        return []

    ms_per_candle = interval_to_milliseconds(interval)
    sorted_times = df["open_time"].sort_values().tolist()

    missing_ranges = []

    for i in range(len(sorted_times) - 1):
        curr = sorted_times[i]
        nxt = sorted_times[i + 1]

        expected_next = curr + ms_per_candle
        if nxt > expected_next:
            missing_ranges.append((expected_next, nxt - ms_per_candle))

    return missing_ranges
