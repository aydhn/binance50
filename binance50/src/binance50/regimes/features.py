import numpy as np
import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeLeakageError


def compute_slope(series: pd.Series, window: int) -> pd.Series:
    x = np.arange(window)

    def linear_fit(y):
        if np.isnan(y).any():
            return np.nan
        coeffs = np.polyfit(x, y, 1)
        return coeffs[0]

    return series.rolling(window=window).apply(linear_fit, raw=True)


def compute_realized_volatility(close: pd.Series, window: int) -> pd.Series:
    log_returns = np.log(close / close.shift(1))
    return log_returns.rolling(window=window).std() * np.sqrt(252 * 24 * 60)


def compute_rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    roll = series.rolling(window=window)
    return (series - roll.mean()) / roll.std()


def compute_bb_width_pct(upper: pd.Series, lower: pd.Series, mid: pd.Series) -> pd.Series:
    return ((upper - lower) / mid) * 100.0


def compute_range_score(df: pd.DataFrame, config: AppConfig) -> pd.Series:
    if "reg_adx_14" in df.columns:
        return np.maximum(0, 100 - df["reg_adx_14"])
    return pd.Series(0, index=df.index)


def add_trend_strength_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if "close" in df.columns:
        for w in config.regimes.features.trend_windows:
            if w <= len(df):
                df[f"reg_trend_slope_{w}"] = compute_slope(df["close"], w)
    if "ADX" in df.columns:
        df[f"reg_adx_{config.regimes.features.adx_period}"] = df["ADX"]
    elif "adx" in df.columns:
        df[f"reg_adx_{config.regimes.features.adx_period}"] = df["adx"]
    elif f"reg_adx_{config.regimes.features.adx_period}" not in df.columns:
        df[f"reg_adx_{config.regimes.features.adx_period}"] = 0.0
    return df


def add_volatility_regime_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    for w in config.regimes.features.volatility_windows:
        if "close" in df.columns:
            df[f"reg_realized_vol_{w}"] = compute_realized_volatility(df["close"], w)
            df[f"reg_realized_vol_z_{w}"] = compute_rolling_zscore(df[f"reg_realized_vol_{w}"], w)

    atr_col = "ATR" if "ATR" in df.columns else "atr" if "atr" in df.columns else None
    if atr_col:
        w = config.regimes.features.atr_period
        df[f"reg_atr_z_{w}"] = compute_rolling_zscore(df[atr_col], w)
    return df


def add_range_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    bb_u, bb_l, bb_m = None, None, None
    for c in df.columns:
        if "upper" in c.lower() and "bb" in c.lower():
            bb_u = c
        if "lower" in c.lower() and "bb" in c.lower():
            bb_l = c
        if "mid" in c.lower() and "bb" in c.lower():
            bb_m = c

    w = config.regimes.features.bb_width_period
    if bb_u and bb_l and bb_m:
        df[f"reg_bb_width_pct_{w}"] = compute_bb_width_pct(df[bb_u], df[bb_l], df[bb_m])
    else:
        df[f"reg_bb_width_pct_{w}"] = 0.0

    for w in config.regimes.features.range_windows:
        df[f"reg_range_score_{w}"] = compute_range_score(df, config)
    return df


def add_volume_regime_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    w = config.regimes.features.volume_window
    if "volume" in df.columns:
        df[f"reg_volume_z_{w}"] = compute_rolling_zscore(df["volume"], w)
    elif "Volume" in df.columns:
        df[f"reg_volume_z_{w}"] = compute_rolling_zscore(df["Volume"], w)
    return df


def add_signal_context_features(
    df: pd.DataFrame, scored_signals_df, config: AppConfig
) -> pd.DataFrame:
    df["reg_signal_confluence_avg"] = 0.0
    df["reg_mtf_alignment_score"] = 0.0
    return df


def validate_regime_feature_frame(df: pd.DataFrame, config: AppConfig) -> None:
    invalid_cols = ["target", "label", "future_return", "next_close", "forward_return"]
    for col in invalid_cols:
        if col in df.columns:
            raise RegimeLeakageError(f"Leakage detected: column {col} found.")


def build_regime_features(
    df: pd.DataFrame, config: AppConfig, scored_signals_df=None
) -> pd.DataFrame:
    df_feat = df.copy()
    df_feat = add_trend_strength_features(df_feat, config)
    df_feat = add_volatility_regime_features(df_feat, config)
    df_feat = add_range_features(df_feat, config)
    df_feat = add_volume_regime_features(df_feat, config)
    df_feat = add_signal_context_features(df_feat, scored_signals_df, config)
    validate_regime_feature_frame(df_feat, config)
    return df_feat
