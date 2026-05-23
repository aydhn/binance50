import pandas as pd
from typing import Dict, List
from binance50.core.exceptions import FeatureGroupError

NON_FEATURE_COLUMNS = {
    "open_time",
    "close_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "market_scope",
    "interval",
    "source",
    "is_closed",
    "is_warmup",
    "feature_set_id",
    "feature_config_hash",
    "generated_at_utc"
}

TARGET_KEYWORDS = ["target", "label", "future", "next", "forward", "return"]

def list_feature_columns(df: pd.DataFrame) -> List[str]:
    """List all feature columns in the dataframe, excluding non-feature columns."""
    return exclude_non_feature_columns(df.columns.tolist())

def exclude_non_feature_columns(columns: List[str]) -> List[str]:
    """Filter out non-feature columns from a list of column names."""
    return [col for col in columns if col not in NON_FEATURE_COLUMNS]

def split_features_by_prefix(columns: List[str], prefix_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Group feature columns based on a prefix mapping."""
    grouped: Dict[str, List[str]] = {group: [] for group in prefix_map}
    ungrouped = []

    for col in columns:
        matched = False
        for group, prefixes in prefix_map.items():
            if any(col.startswith(p) for p in prefixes):
                grouped[group].append(col)
                matched = True
                break

        if not matched:
            ungrouped.append(col)

    if ungrouped:
        grouped["ungrouped"] = ungrouped

    return grouped

def assert_no_target_like_columns(columns: List[str]) -> None:
    """Ensure no target-like columns exist in the feature set."""
    violations = []
    for col in columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in TARGET_KEYWORDS):
            violations.append(col)

    if violations:
        raise FeatureGroupError(f"Target-like or future columns detected and are prohibited in features: {violations}")
