from enum import StrEnum

import pandas as pd
from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.exceptions import PivotDetectionError


class PivotType(StrEnum):
    high = "high"
    low = "low"


class PivotPoint(BaseModel):
    symbol: str
    interval: str
    open_time: pd.Timestamp
    index: int
    pivot_type: PivotType
    value: float
    source_column: str
    prominence_pct: float
    confirmed: bool
    warnings: list[str] = []

    class Config:
        arbitrary_types_allowed = True


def detect_causal_pivot_highs(
    series: pd.Series, left_window: int, min_prominence_pct: float, min_distance_bars: int
) -> list[PivotPoint]:
    """Detect local highs strictly using causal (backward-looking) window."""
    if left_window < 1:
        raise PivotDetectionError("left_window must be >= 1")

    pivots = []
    values = series.values
    indices = series.index

    # We can only confirm a pivot if we have a causal window.
    # Here, "confirmed" simply means it was the highest in the past `left_window` bars AND the current bar is lower,
    # acting as a basic causal peak detection.
    # In a stricter causal model, bar `i` is a pivot if `i - 1` is highest in `i - 1 - left_window` to `i - 1`, and `i < i - 1`.

    last_pivot_idx = -min_distance_bars - 1

    for i in range(left_window + 1, len(values)):
        candidate_idx = i - 1
        candidate_val = values[candidate_idx]

        # Check causal window (left side)
        window_start = max(0, candidate_idx - left_window)
        left_vals = values[window_start:candidate_idx]

        if len(left_vals) == 0:
            continue

        left_max = left_vals.max()

        # Causal confirmation: candidate is strictly > left window, and current bar `i` is < candidate
        if candidate_val > left_max and values[i] < candidate_val:
            # Check prominence
            prominence = 0.0
            if left_max != 0:
                prominence = (candidate_val - left_max) / abs(left_max)

            if prominence >= min_prominence_pct:
                if candidate_idx - last_pivot_idx >= min_distance_bars:
                    pivots.append(
                        PivotPoint(
                            symbol="unknown",  # To be filled by caller
                            interval="unknown",  # To be filled by caller
                            open_time=(
                                indices[candidate_idx]
                                if isinstance(indices, pd.DatetimeIndex)
                                else pd.Timestamp.utcnow()
                            ),
                            index=candidate_idx,
                            pivot_type=PivotType.high,
                            value=float(candidate_val),
                            source_column="unknown",  # To be filled by caller
                            prominence_pct=float(prominence),
                            confirmed=True,
                        )
                    )
                    last_pivot_idx = candidate_idx

    return pivots


def detect_causal_pivot_lows(
    series: pd.Series, left_window: int, min_prominence_pct: float, min_distance_bars: int
) -> list[PivotPoint]:
    """Detect local lows strictly using causal (backward-looking) window."""
    if left_window < 1:
        raise PivotDetectionError("left_window must be >= 1")

    pivots = []
    values = series.values
    indices = series.index

    last_pivot_idx = -min_distance_bars - 1

    for i in range(left_window + 1, len(values)):
        candidate_idx = i - 1
        candidate_val = values[candidate_idx]

        window_start = max(0, candidate_idx - left_window)
        left_vals = values[window_start:candidate_idx]

        if len(left_vals) == 0:
            continue

        left_min = left_vals.min()

        if candidate_val < left_min and values[i] > candidate_val:
            prominence = 0.0
            if left_min != 0:
                prominence = (left_min - candidate_val) / abs(left_min)

            if prominence >= min_prominence_pct:
                if candidate_idx - last_pivot_idx >= min_distance_bars:
                    pivots.append(
                        PivotPoint(
                            symbol="unknown",
                            interval="unknown",
                            open_time=(
                                indices[candidate_idx]
                                if isinstance(indices, pd.DatetimeIndex)
                                else pd.Timestamp.utcnow()
                            ),
                            index=candidate_idx,
                            pivot_type=PivotType.low,
                            value=float(candidate_val),
                            source_column="unknown",
                            prominence_pct=float(prominence),
                            confirmed=True,
                        )
                    )
                    last_pivot_idx = candidate_idx

    return pivots


def enforce_min_pivot_distance(
    pivots: list[PivotPoint], min_distance_bars: int
) -> list[PivotPoint]:
    """Filter pivots to ensure minimum distance between same-type pivots."""
    if not pivots:
        return []

    pivots = sorted(pivots, key=lambda p: p.index)
    result = [pivots[0]]

    for current in pivots[1:]:
        last = result[-1]

        if current.pivot_type == last.pivot_type:
            if current.index - last.index >= min_distance_bars:
                result.append(current)
            else:
                # Same type, too close. Keep the more extreme one.
                if (
                    current.pivot_type == PivotType.high
                    and current.value > last.value
                    or current.pivot_type == PivotType.low
                    and current.value < last.value
                ):
                    result[-1] = current
        else:
            result.append(current)

    return result


def detect_price_pivots(
    df: pd.DataFrame, source_column: str, config: AppConfig
) -> list[PivotPoint]:
    if source_column not in df.columns:
        raise PivotDetectionError(f"Source column {source_column} not found in dataframe")

    cfg = config.indicator_v2.pivots
    if not cfg.enabled:
        return []

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "unknown"
    interval = df["interval"].iloc[0] if "interval" in df.columns else "unknown"

    # In case index is not datetime, but we have open_time
    if "open_time" in df.columns and not isinstance(df.index, pd.DatetimeIndex):
        series = df.set_index("open_time")[source_column]
    else:
        series = df[source_column]

    highs = detect_causal_pivot_highs(
        series, cfg.left_window, cfg.min_prominence_pct, cfg.min_distance_bars
    )
    lows = detect_causal_pivot_lows(
        series, cfg.left_window, cfg.min_prominence_pct, cfg.min_distance_bars
    )

    pivots = highs + lows
    for p in pivots:
        p.symbol = symbol
        p.interval = interval
        p.source_column = source_column

    # Sort and enforce alternating/distance if needed, but for now just basic distance
    pivots = sorted(pivots, key=lambda p: p.index)
    return enforce_min_pivot_distance(pivots, cfg.min_distance_bars)[: cfg.max_pivots_per_series]


def detect_indicator_pivots(
    df: pd.DataFrame, indicator_column: str, config: AppConfig
) -> list[PivotPoint]:
    # Indicator pivots generally don't require the same strict prominence as price, but we use same logic
    return detect_price_pivots(df, indicator_column, config)


def pivots_to_dataframe(pivots: list[PivotPoint]) -> pd.DataFrame:
    if not pivots:
        return pd.DataFrame()

    data = []
    for p in pivots:
        data.append(
            {
                "symbol": p.symbol,
                "interval": p.interval,
                "open_time": p.open_time,
                "index": p.index,
                "pivot_type": p.pivot_type.value,
                "value": p.value,
                "source_column": p.source_column,
                "prominence_pct": p.prominence_pct,
                "confirmed": p.confirmed,
            }
        )
    return pd.DataFrame(data)


def add_pivot_flags(df: pd.DataFrame, pivots: list[PivotPoint], prefix: str) -> pd.DataFrame:
    df = df.copy()

    high_col = f"{prefix}_pivot_high"
    low_col = f"{prefix}_pivot_low"

    df[high_col] = False
    df[low_col] = False

    if not pivots:
        return df

    high_indices = [p.index for p in pivots if p.pivot_type == PivotType.high]
    low_indices = [p.index for p in pivots if p.pivot_type == PivotType.low]

    if high_indices:
        df.iloc[high_indices, df.columns.get_loc(high_col)] = True
    if low_indices:
        df.iloc[low_indices, df.columns.get_loc(low_col)] = True

    return df
