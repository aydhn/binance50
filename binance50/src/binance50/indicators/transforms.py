import warnings

import numpy as np
import pandas as pd


def typical_price(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    return (high + low + close) / 3.0


def median_price(high: pd.Series, low: pd.Series) -> pd.Series:
    return (high + low) / 2.0


def weighted_close(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    return (high + low + (close * 2.0)) / 4.0


def hl_range(high: pd.Series, low: pd.Series) -> pd.Series:
    return high - low


def oc_change(open_price: pd.Series, close_price: pd.Series) -> pd.Series:
    return close_price - open_price


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    # Concatenate and max along axis 1
    df = pd.concat([tr1, tr2, tr3], axis=1)
    res = df.max(axis=1)
    if len(res) > 0:
        res.iloc[0] = np.nan
    return res


def returns(close: pd.Series, period: int = 1) -> pd.Series:
    # Ensure past lookback (shift period > 0)
    if period <= 0:
        raise ValueError("Return period must be > 0 for past returns to avoid lookahead bias")
    return close.pct_change(periods=period)


def log_returns(close: pd.Series, period: int = 1) -> pd.Series:
    if period <= 0:
        raise ValueError("Return period must be > 0")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Ensure we don't take log of <= 0
        safe_close = close.where(close > 0, np.nan)
        return np.log(safe_close / safe_close.shift(period))


def rolling_zscore(series: pd.Series, period: int) -> pd.Series:
    if period <= 1:
        return pd.Series(0.0, index=series.index)

    mean = series.rolling(window=period, min_periods=period).mean()
    std = series.rolling(window=period, min_periods=period).std()

    # safe_divide replaces nan with 0.0, we want to keep nan where std is nan
    res = safe_divide(series - mean, std)
    res[std.isna()] = np.nan
    return res


def rolling_min(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).min()


def rolling_max(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).max()


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    # Avoid inf on divide by zero
    result = numerator / denominator.replace(0, np.nan)
    return result.fillna(0.0)  # Or keep nan, but fillna(0) is common for safe divide
