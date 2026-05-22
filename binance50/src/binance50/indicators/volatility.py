import numpy as np
import pandas as pd

from binance50.indicators.transforms import log_returns, true_range


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = true_range(high, low, close)

    def _smma(series, length):
        res = series.ewm(alpha=1/length, adjust=False, min_periods=length).mean()
        sma_val = series.rolling(window=length, min_periods=length).mean()
        mask = ~res.isna()
        first_valid = mask.idxmax() if mask.any() else None
        if first_valid is not None:
             res.loc[first_valid] = sma_val.loc[first_valid]
        return res

    res = _smma(tr, period)
    return pd.Series(res, index=close.index, name=f"vol_atr_{period}")

def natr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    atr_vals = atr(high, low, close, period)
    res = 100 * atr_vals / close.replace(0, np.nan)
    return pd.Series(res, index=close.index, name=f"vol_natr_{period}")

def bollinger_bands(close: pd.Series, period: int = 20, stddev: float = 2.0) -> pd.DataFrame:
    mid = close.rolling(window=period, min_periods=period).mean()
    std = close.rolling(window=period, min_periods=period).std()

    upper = mid + (std * stddev)
    lower = mid - (std * stddev)

    return pd.DataFrame({
        f"vol_bb_mid_{period}_{int(stddev)}": mid,
        f"vol_bb_upper_{period}_{int(stddev)}": upper,
        f"vol_bb_lower_{period}_{int(stddev)}": lower
    })

def bollinger_bandwidth(close: pd.Series, period: int = 20, stddev: float = 2.0) -> pd.Series:
    bb = bollinger_bands(close, period, stddev)
    upper = bb[f"vol_bb_upper_{period}_{int(stddev)}"]
    lower = bb[f"vol_bb_lower_{period}_{int(stddev)}"]
    mid = bb[f"vol_bb_mid_{period}_{int(stddev)}"]

    res = 100 * (upper - lower) / mid.replace(0, np.nan)
    return pd.Series(res, index=close.index, name=f"vol_bb_width_{period}_{int(stddev)}")

def keltner_channels(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20, atr_period: int = 14, multiplier: float = 2.0) -> pd.DataFrame:
    tp = (high + low + close) / 3.0
    ema_tp = tp.ewm(span=period, adjust=False, min_periods=period).mean()

    atr_vals = atr(high, low, close, atr_period)

    upper = ema_tp + (multiplier * atr_vals)
    lower = ema_tp - (multiplier * atr_vals)

    return pd.DataFrame({
        f"vol_kc_mid_{period}_{atr_period}_{int(multiplier)}": ema_tp,
        f"vol_kc_upper_{period}_{atr_period}_{int(multiplier)}": upper,
        f"vol_kc_lower_{period}_{atr_period}_{int(multiplier)}": lower
    })

def donchian_channels(high: pd.Series, low: pd.Series, period: int = 20) -> pd.DataFrame:
    upper = high.rolling(window=period, min_periods=period).max()
    lower = low.rolling(window=period, min_periods=period).min()

    return pd.DataFrame({
        f"vol_donchian_high_{period}": upper,
        f"vol_donchian_low_{period}": lower
    })

def rolling_std(close: pd.Series, period: int = 20) -> pd.Series:
    res = close.rolling(window=period, min_periods=period).std()
    return pd.Series(res, index=close.index, name=f"vol_rolling_std_{period}")

def realized_volatility(close: pd.Series, period: int = 20) -> pd.Series:
    # Uses natural log returns
    lr = log_returns(close, 1)
    res = lr.rolling(window=period, min_periods=period).std() * np.sqrt(365 * 24 * 60) # Assuming 1m data annualized? Actually, let's keep it simple standard dev of returns
    return pd.Series(res, index=close.index, name=f"vol_realized_{period}")
