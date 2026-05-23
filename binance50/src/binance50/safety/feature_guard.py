from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import FeatureQualityError, IndicatorV2Error
from binance50.indicators.feature_groups import FeatureGroup


def assert_feature_config_safe(config: AppConfig) -> None:
    cfg = config.indicator_v2
    if cfg.max_feature_columns > 5000:
        raise IndicatorV2Error("max_feature_columns must not exceed 5000")
    if not cfg.prevent_lookahead_bias:
        raise IndicatorV2Error("prevent_lookahead_bias must be True")


def assert_feature_dataframe_safe(df: pd.DataFrame, config: AppConfig) -> None:
    assert_no_target_or_future_features(df)
    assert_feature_count_within_limit(df, config)

    # Check for secret-like column names
    secret_words = ["api_key", "secret", "token", "signature", "password"]
    for col in df.columns:
        col_lower = col.lower()
        if any(secret in col_lower for secret in secret_words):
            raise FeatureQualityError(f"Secret-like column name detected: {col}")


def assert_no_target_or_future_features(df: pd.DataFrame) -> None:
    from binance50.features.grouping import TARGET_KEYWORDS

    violations = []
    for col in df.columns:
        col_lower = col.lower()
        if any(k in col_lower for k in TARGET_KEYWORDS):
            violations.append(col)

    if violations:
        raise FeatureQualityError(f"Prohibited target/future columns found: {violations}")


def assert_feature_count_within_limit(df: pd.DataFrame, config: AppConfig) -> None:
    limit = config.indicator_v2.max_feature_columns
    if len(df.columns) > limit:
        raise FeatureQualityError(f"Feature count {len(df.columns)} exceeds limit {limit}")


def assert_feature_groups_safe(groups: list[FeatureGroup], config: AppConfig) -> None:
    pass


def build_feature_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "prevent_lookahead_bias": config.indicator_v2.prevent_lookahead_bias,
        "reject_future_columns": config.indicator_v2.reject_future_columns,
        "max_feature_columns": config.indicator_v2.max_feature_columns,
    }
