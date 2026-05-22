import numpy as np
import pandas as pd


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    delta = close.diff()
    direction = np.sign(delta)

    # If delta is 0, direction is 0, meaning no volume is added/subtracted
    # But OBV traditionally keeps previous value. With np.sign, it evaluates to 0 * volume = 0
    # Wait, cumulative sum:
    direction_s = pd.Series(direction, index=close.index).fillna(1) # Start with positive

    obv_vol = direction_s * volume
    res = obv_vol.cumsum()
    return pd.Series(res, index=close.index, name="volu_obv")

def volume_sma(volume: pd.Series, period: int) -> pd.Series:
    res = volume.rolling(window=period, min_periods=period).mean()
    return pd.Series(res, index=volume.index, name=f"volu_volume_sma_{period}")

def volume_ema(volume: pd.Series, period: int) -> pd.Series:
    res = volume.ewm(span=period, adjust=False, min_periods=period).mean()
    return pd.Series(res, index=volume.index, name=f"volu_volume_ema_{period}")

def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 20) -> pd.Series:
    tp = (high + low + close) / 3.0
    tp_vol = tp * volume

    sum_tp_vol = tp_vol.rolling(window=period, min_periods=period).sum()
    sum_vol = volume.rolling(window=period, min_periods=period).sum()

    res = sum_tp_vol / sum_vol.replace(0, np.nan)
    return pd.Series(res, index=close.index, name=f"volu_vwap_{period}")

def mfi(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
    tp = (high + low + close) / 3.0
    rmf = tp * volume

    tp_diff = tp.diff()

    pos_mf = np.where(tp_diff > 0, rmf, 0.0)
    neg_mf = np.where(tp_diff < 0, rmf, 0.0)

    pos_mf_s = pd.Series(pos_mf, index=close.index)
    neg_mf_s = pd.Series(neg_mf, index=close.index)

    pos_sum = pos_mf_s.rolling(window=period, min_periods=period).sum()
    neg_sum = neg_mf_s.rolling(window=period, min_periods=period).sum()

    money_ratio = pos_sum / neg_sum.replace(0, np.nan)

    res = 100 - (100 / (1 + money_ratio))
    res[neg_sum == 0] = 100.0 # If no negative flow, MFI is 100

    return pd.Series(res, index=close.index, name=f"volu_mfi_{period}")

def cmf(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 20) -> pd.Series:
    ad = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    mfv = ad * volume

    sum_mfv = mfv.rolling(window=period, min_periods=period).sum()
    sum_vol = volume.rolling(window=period, min_periods=period).sum()

    res = sum_mfv / sum_vol.replace(0, np.nan)
    return pd.Series(res, index=close.index, name=f"volu_cmf_{period}")

def accumulation_distribution_line(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    ad = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    mfv = ad * volume

    res = mfv.cumsum()
    return pd.Series(res, index=close.index, name="volu_adl")

def volume_rate_of_change(volume: pd.Series, period: int = 10) -> pd.Series:
    res = 100 * (volume - volume.shift(period)) / volume.shift(period).replace(0, np.nan)
    return pd.Series(res, index=volume.index, name=f"volu_vroc_{period}")
