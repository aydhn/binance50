import pandas as pd
from typing import List
from binance50.core.exceptions import IndicatorV2Error

def lag_features(df: pd.DataFrame, columns: List[str], lags: List[int]) -> pd.DataFrame:
    """Safely apply lag to features, ensuring no negative (future) lags."""
    if not columns or not lags:
        return df

    for lag in lags:
        if lag <= 0:
            raise IndicatorV2Error(f"Lag must be positive, got {lag}")

    result_df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        for lag in lags:
            new_col = f"lag_{lag}_{col}"
            result_df[new_col] = df[col].shift(lag)

    return result_df

def rolling_feature_stats(df: pd.DataFrame, columns: List[str], periods: List[int]) -> pd.DataFrame:
    """Safely apply rolling stats to features, strictly non-centered."""
    if not columns or not periods:
        return df

    for period in periods:
        if period <= 0:
            raise IndicatorV2Error(f"Rolling period must be positive, got {period}")

    result_df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        for period in periods:
            new_col_mean = f"roll_mean_{period}_{col}"
            new_col_std = f"roll_std_{period}_{col}"

            # Strict center=False to prevent lookahead
            rolling = df[col].rolling(window=period, center=False)
            result_df[new_col_mean] = rolling.mean()
            result_df[new_col_std] = rolling.std()

    return result_df

def expanding_feature_stats(df: pd.DataFrame, columns: List[str], min_periods: int = 1) -> pd.DataFrame:
    """Apply expanding window stats safely."""
    if not columns:
        return df

    result_df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        expanding = df[col].expanding(min_periods=min_periods)

        new_col_mean = f"exp_mean_{col}"
        new_col_std = f"exp_std_{col}"

        result_df[new_col_mean] = expanding.mean()
        result_df[new_col_std] = expanding.std()

    return result_df
