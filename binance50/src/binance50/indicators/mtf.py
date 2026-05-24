from typing import Any

import pandas as pd
from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.exceptions import MTFAlignmentError, MTFLookaheadError


class MTFAlignmentRequest(BaseModel):
    symbol: str
    market_scope: str
    base_interval: str
    higher_interval: str
    base_df_hash: str
    higher_df_hash: str
    tolerance_ms: int
    require_higher_tf_closed: bool
    alignment_method: str


class MTFAlignmentResult(BaseModel):
    request: MTFAlignmentRequest
    aligned_df: pd.DataFrame
    matched_rows: int
    unmatched_rows: int
    stale_rows: int
    metadata: dict[str, Any]
    warnings: list[str] = []

    class Config:
        arbitrary_types_allowed = True


def compute_mtf_tolerance_ms(
    base_interval: str, higher_interval: str, max_alignment_tolerance_bars: int
) -> int:
    # A simple mock parser. In a real app we'd convert intervals to ms.
    # 1m = 60000, 1h = 3600000
    interval_map = {
        "1m": 60000,
        "5m": 300000,
        "15m": 900000,
        "1h": 3600000,
        "4h": 14400000,
        "1d": 86400000,
    }
    interval_map.get(base_interval, 60000)
    higher_ms = interval_map.get(higher_interval, 3600000)

    return higher_ms * max_alignment_tolerance_bars


def prepare_higher_tf_features(
    higher_df: pd.DataFrame, higher_interval: str, config: AppConfig
) -> pd.DataFrame:
    df = higher_df.copy()
    if config.indicator_v2.mtf.add_higher_tf_prefix:
        prefix = config.indicator_v2.mtf.prefix_template.format(interval=higher_interval)
        rename_dict = {}
        from binance50.features.grouping import NON_FEATURE_COLUMNS

        for col in df.columns:
            if col not in NON_FEATURE_COLUMNS and col != "open_time" and col != "close_time":
                rename_dict[col] = f"{prefix}{col}"
        df = df.rename(columns=rename_dict)
    return df


def align_higher_tf_to_base(
    base_df: pd.DataFrame, higher_df: pd.DataFrame, request: MTFAlignmentRequest, config: AppConfig
) -> MTFAlignmentResult:
    cfg = config.indicator_v2.mtf

    if cfg.disallow_forward_alignment and request.alignment_method != "asof_backward":
        raise MTFLookaheadError(f"Alignment method {request.alignment_method} is disallowed")

    if "open_time" not in base_df.columns or "close_time" not in higher_df.columns:
        raise MTFAlignmentError("Missing required time columns for alignment")

    if request.require_higher_tf_closed and "is_closed" in higher_df.columns:
        h_df = higher_df[higher_df["is_closed"]].copy()
    else:
        h_df = higher_df.copy()

    # Sort to ensure asof works
    base_df = base_df.sort_values("open_time")
    h_df = h_df.sort_values("close_time")

    # We match base open_time against higher close_time using backward
    # This means for a base bar opening at 10:00, we look for a higher bar that closed AT OR BEFORE 10:00.

    aligned = pd.merge_asof(
        base_df,
        h_df,
        left_on="open_time",
        right_on="close_time",
        direction="backward",
        tolerance=(
            pd.Timedelta(milliseconds=request.tolerance_ms) if request.tolerance_ms > 0 else None
        ),
        suffixes=("", "_higher"),
    )

    matched = (
        aligned["close_time_higher"].notna().sum()
        if "close_time_higher" in aligned.columns
        else aligned["close_time"].notna().sum()
    )
    unmatched = len(aligned) - matched

    if cfg.drop_unmatched_rows:
        if "close_time_higher" in aligned.columns:
            aligned = aligned.dropna(
                subset=[
                    "close_time_higher" if "close_time_higher" in aligned.columns else "close_time"
                ]
            )
    elif cfg.mark_unmatched_rows:
        aligned["mtf_unmatched"] = (
            aligned["close_time_higher"].isna()
            if "close_time_higher" in aligned.columns
            else aligned["close_time"].isna()
        )

    validate_mtf_no_future_alignment(base_df, aligned, "close_time_higher")

    # Remove extra join keys
    if "close_time_higher" in aligned.columns:
        aligned = aligned.drop(columns=["close_time_higher"])

    if "open_time_higher" in aligned.columns:
        aligned = aligned.drop(columns=["open_time_higher"])

    result = MTFAlignmentResult(
        request=request,
        aligned_df=aligned,
        matched_rows=int(matched),
        unmatched_rows=int(unmatched),
        stale_rows=0,
        metadata={},
    )

    return result


def validate_mtf_no_future_alignment(
    base_df: pd.DataFrame, aligned_df: pd.DataFrame, higher_time_column: str
) -> None:
    if higher_time_column not in aligned_df.columns:
        return

    # higher close time must be <= base open time
    future_leaks = aligned_df[aligned_df[higher_time_column] > aligned_df["open_time"]]

    if len(future_leaks) > 0:
        raise MTFLookaheadError(
            f"Found {len(future_leaks)} rows where higher TF data is from the future"
        )


def build_mtf_alignment_metadata(result: MTFAlignmentResult) -> dict:
    return {
        "base_interval": result.request.base_interval,
        "higher_interval": result.request.higher_interval,
        "matched": result.matched_rows,
        "unmatched": result.unmatched_rows,
        "tolerance_ms": result.request.tolerance_ms,
    }
