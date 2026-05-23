import numpy as np
import pandas as pd

from binance50.indicators.transforms import true_range


def sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(window=period, min_periods=period).mean()


def ema(close: pd.Series, period: int) -> pd.Series:
    return close.ewm(span=period, adjust=False, min_periods=period).mean()


def wma(close: pd.Series, period: int) -> pd.Series:
    weights = np.arange(1, period + 1)

    def _wma(x):
        return np.dot(x, weights) / weights.sum()

    return close.rolling(window=period, min_periods=period).apply(_wma, raw=True)


def dema(close: pd.Series, period: int) -> pd.Series:
    ema1 = ema(close, period)
    ema2 = ema(ema1, period)
    return 2 * ema1 - ema2


def tema(close: pd.Series, period: int) -> pd.Series:
    ema1 = ema(close, period)
    ema2 = ema(ema1, period)
    ema3 = ema(ema2, period)
    return 3 * ema1 - 3 * ema2 + ema3


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)

    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    macd_hist = macd_line - signal_line

    return pd.DataFrame(
        {
            f"trend_macd_{fast}_{slow}_{signal}": macd_line,
            f"trend_macd_signal_{fast}_{slow}_{signal}": signal_line,
            f"trend_macd_hist_{fast}_{slow}_{signal}": macd_hist,
        }
    )


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
    # Wilder's smoothing
    def _smma(series, length):
        res = series.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
        # Wilder's initial value is the simple moving average
        sma_val = series.rolling(window=length, min_periods=length).mean()
        # Mix them
        mask = ~res.isna()
        first_valid = mask.idxmax() if mask.any() else None
        if first_valid is not None:
            res.loc[first_valid] = sma_val.loc[first_valid]
        return res

    tr = true_range(high, low, close)

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    plus_dm_s = pd.Series(plus_dm, index=high.index)
    minus_dm_s = pd.Series(minus_dm, index=high.index)

    atr = _smma(tr, period)
    plus_di = 100 * _smma(plus_dm_s, period) / atr
    minus_di = 100 * _smma(minus_dm_s, period) / atr

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    dx_smoothed = _smma(dx, period)

    return pd.DataFrame(
        {
            f"trend_adx_{period}": dx_smoothed,
            f"trend_plus_di_{period}": plus_di,
            f"trend_minus_di_{period}": minus_di,
        }
    )


def aroon(high: pd.Series, low: pd.Series, period: int = 14) -> pd.DataFrame:
    aroon_up = high.rolling(window=period + 1, min_periods=period + 1).apply(
        lambda x: 100 * (period - (period - x.argmax())) / period, raw=True
    )
    aroon_down = low.rolling(window=period + 1, min_periods=period + 1).apply(
        lambda x: 100 * (period - (period - x.argmin())) / period, raw=True
    )
    aroon_osc = aroon_up - aroon_down

    return pd.DataFrame(
        {
            f"trend_aroon_up_{period}": aroon_up,
            f"trend_aroon_down_{period}": aroon_down,
            f"trend_aroon_osc_{period}": aroon_osc,
        }
    )


def price_above_ma(close: pd.Series, ma: pd.Series) -> pd.Series:
    return (close > ma).astype(int)


def ma_slope(ma: pd.Series, period: int = 1) -> pd.Series:
    return (ma - ma.shift(period)) / period
