import hashlib
import json
from typing import Any

import pandas as pd


def compute_feature_set_hash(df: pd.DataFrame, feature_columns: list[str]) -> str:
    """Compute a deterministic hash for a feature set dataframe."""
    if df.empty or not feature_columns:
        return hashlib.sha256(b"empty").hexdigest()

    # In a real app we'd want a very fast hash, but this serves for deterministic ID
    # We hash the column names and some fundamental stats to detect changes
    stats_df = df[feature_columns].describe().to_json()
    hasher = hashlib.sha256()
    hasher.update(",".join(sorted(feature_columns)).encode("utf-8"))
    hasher.update(stats_df.encode("utf-8"))

    return hasher.hexdigest()


def compute_config_hash(config_section: dict[str, Any]) -> str:
    """Compute a hash of the configuration to track provenance."""
    config_str = json.dumps(config_section, sort_keys=True)
    return hashlib.sha256(config_str.encode("utf-8")).hexdigest()


def summarize_feature_nan_ratios(df: pd.DataFrame, feature_columns: list[str]) -> dict[str, float]:
    """Calculate the ratio of NaN values for each feature column."""
    if df.empty or not feature_columns:
        return {}

    nan_counts = df[feature_columns].isna().sum()
    total_rows = len(df)

    return {col: float(count / total_rows) for col, count in nan_counts.items()}


def summarize_feature_ranges(
    df: pd.DataFrame, feature_columns: list[str]
) -> dict[str, dict[str, float]]:
    """Summarize min, max, mean for numeric features."""
    if df.empty or not feature_columns:
        return {}

    ranges = {}
    numeric_df = df[feature_columns].select_dtypes(include=["number"])

    for col in numeric_df.columns:
        ranges[col] = {
            "min": float(numeric_df[col].min()),
            "max": float(numeric_df[col].max()),
            "mean": float(numeric_df[col].mean()),
        }

    return ranges
