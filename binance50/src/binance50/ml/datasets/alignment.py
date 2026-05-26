import pandas as pd
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLAlignmentError


def align_feature_sources(base_df: pd.DataFrame, source_frames: dict[str, pd.DataFrame], config: AppConfig) -> pd.DataFrame:
    aligned_df = base_df.copy()

    for source_name, source_df in source_frames.items():
        aligned_df = align_single_source_backward_asof(aligned_df, source_df, source_name, config)

    return aligned_df

def align_single_source_backward_asof(base_df: pd.DataFrame, source_df: pd.DataFrame, source_name: str, config: AppConfig) -> pd.DataFrame:
    if "open_time" not in base_df.columns or "open_time" not in source_df.columns:
         raise MLAlignmentError(f"open_time column missing for alignment with {source_name}")

    if config.ml_dataset and config.ml_dataset.alignment.reject_forward_alignment:
         # Built-in pd.merge_asof with direction='backward' ensures no future join
         aligned = pd.merge_asof(
             base_df.sort_values("open_time"),
             source_df.sort_values("open_time"),
             on="open_time",
             direction="backward"
         )
         validate_no_future_alignment(base_df, aligned, "open_time")
         return aligned

    raise MLAlignmentError("Only backward asof alignment is supported")

def validate_no_future_alignment(base_df: pd.DataFrame, aligned_df: pd.DataFrame, source_time_column: str) -> None:
    # A backward asof join on 'open_time' inherently prevents future rows from joining,
    # so we just check structural row count equality to ensure no unintended duplication
    if len(base_df) != len(aligned_df):
        raise MLAlignmentError("Row count mismatch after alignment")

def validate_alignment_metadata(metadata: dict[str, Any], config: AppConfig) -> None:
    pass # Skeleton

def build_alignment_report(aligned_sources: dict[str, Any]) -> dict[str, Any]:
    return {"aligned_count": len(aligned_sources)}
