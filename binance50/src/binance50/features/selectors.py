import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import FeatureGroupError
from binance50.features.grouping import exclude_non_feature_columns


def select_features_by_group(
    df: pd.DataFrame, groups: list[str], config: AppConfig
) -> pd.DataFrame:
    """Select features belonging to specific groups based on config prefixes."""
    if not config.indicator_v2.feature_groups.enabled:
        raise FeatureGroupError("Feature groups are disabled in config")

    all_features = exclude_non_feature_columns(df.columns.tolist())
    selected_cols = []

    group_configs = config.indicator_v2.feature_groups.groups
    for group in groups:
        if group not in group_configs:
            raise FeatureGroupError(f"Group {group} not defined in config")

        prefixes = group_configs[group].get("prefixes", [])
        for col in all_features:
            if any(col.startswith(p) for p in prefixes) and col not in selected_cols:
                selected_cols.append(col)

    non_features = [c for c in df.columns if c not in all_features]
    return df[non_features + selected_cols].copy()


def select_features_by_prefix(df: pd.DataFrame, prefixes: list[str]) -> pd.DataFrame:
    """Select features by matching prefix."""
    all_features = exclude_non_feature_columns(df.columns.tolist())
    selected_cols = [col for col in all_features if any(col.startswith(p) for p in prefixes)]

    non_features = [c for c in df.columns if c not in all_features]
    return df[non_features + selected_cols].copy()


def select_safe_features(df: pd.DataFrame, registry, config: AppConfig) -> pd.DataFrame:
    """Select only features registered and marked as safe for training/backtest."""
    all_features = exclude_non_feature_columns(df.columns.tolist())
    safe_cols = []

    for col in all_features:
        meta = registry.get_feature(col)
        if meta and meta.is_safe_for_training and meta.is_safe_for_backtest:
            safe_cols.append(col)

    non_features = [c for c in df.columns if c not in all_features]
    return df[non_features + safe_cols].copy()


def drop_unsafe_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Drop any features that might introduce lookahead or are target-like."""
    all_features = exclude_non_feature_columns(df.columns.tolist())

    # Check for target-like
    unsafe_cols = []
    from binance50.features.grouping import TARGET_KEYWORDS

    for col in all_features:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in TARGET_KEYWORDS):
            unsafe_cols.append(col)

    if not unsafe_cols:
        return df.copy()

    return df.drop(columns=unsafe_cols)
