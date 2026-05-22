import numpy as np
import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()

    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)

    up_s = pd.Series(up, index=close.index)
    down_s = pd.Series(down, index=close.index)

    def _smma(series, length):
        res = series.ewm(alpha=1/length, adjust=False, min_periods=length).mean()
        sma_val = series.rolling(window=length, min_periods=length).mean()
        mask = ~res.isna()
        first_valid = mask.idxmax() if mask.any() else None
        if first_valid is not None:
             res.loc[first_valid] = sma_val.loc[first_valid]
        return res

    rs_up = _smma(up_s, period)
    rs_down = _smma(down_s, period)

    # Avoid divide by zero
    rs_down = rs_down.replace(0, np.nan)
    rs = rs_up / rs_down

    res = 100 - (100 / (1 + rs))
    # If down is 0 but up is not, RSI is 100
    res[rs_down.isna() & (rs_up > 0)] = 100.0
    res[(rs_down.isna()) & (rs_up == 0)] = 50.0

    return pd.Series(res, index=close.index, name=f"mom_rsi_{period}")

def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3, smooth_k: int = 3) -> pd.DataFrame:
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()

    fast_k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)

    if smooth_k > 1:
        slow_k = fast_k.rolling(window=smooth_k, min_periods=smooth_k).mean()
    else:
        slow_k = fast_k

    slow_d = slow_k.rolling(window=d_period, min_periods=d_period).mean()

    return pd.DataFrame({
        f"mom_stoch_k_{k_period}_{d_period}_{smooth_k}": slow_k,
        f"mom_stoch_d_{k_period}_{d_period}_{smooth_k}": slow_d
    })

def stoch_rsi(close: pd.Series, rsi_period: int = 14, stoch_period: int = 14, k_period: int = 3, d_period: int = 3) -> pd.DataFrame:
    rsi_vals = rsi(close, rsi_period)

    lowest_rsi = rsi_vals.rolling(window=stoch_period, min_periods=stoch_period).min()
    highest_rsi = rsi_vals.rolling(window=stoch_period, min_periods=stoch_period).max()

    stoch_rsi_k = 100 * (rsi_vals - lowest_rsi) / (highest_rsi - lowest_rsi).replace(0, np.nan)
    stoch_rsi_k = stoch_rsi_k.rolling(window=k_period, min_periods=k_period).mean()
    stoch_rsi_d = stoch_rsi_k.rolling(window=d_period, min_periods=d_period).mean()

    return pd.DataFrame({
        f"mom_stoch_rsi_k_{rsi_period}_{stoch_period}_{k_period}_{d_period}": stoch_rsi_k,
        f"mom_stoch_rsi_d_{rsi_period}_{stoch_period}_{k_period}_{d_period}": stoch_rsi_d
    })

def roc(close: pd.Series, period: int = 10) -> pd.Series:
    res = 100 * (close - close.shift(period)) / close.shift(period).replace(0, np.nan)
    return pd.Series(res, index=close.index, name=f"mom_roc_{period}")

def momentum(close: pd.Series, period: int = 10) -> pd.Series:
    res = close - close.shift(period)
    return pd.Series(res, index=close.index, name=f"mom_mom_{period}")

def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    tp = (high + low + close) / 3.0
    sma_tp = tp.rolling(window=period, min_periods=period).mean()

    def _mad(x):
        return np.mean(np.abs(x - np.mean(x)))

    mad = tp.rolling(window=period, min_periods=period).apply(_mad, raw=True)

    res = (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
    return pd.Series(res, index=close.index, name=f"mom_cci_{period}")

def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    highest_high = high.rolling(window=period, min_periods=period).max()
    lowest_low = low.rolling(window=period, min_periods=period).min()

    res = -100 * (highest_high - close) / (highest_high - lowest_low).replace(0, np.nan)
    return pd.Series(res, index=close.index, name=f"mom_willr_{period}")
