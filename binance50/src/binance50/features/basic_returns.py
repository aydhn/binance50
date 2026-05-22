import pandas as pd

from binance50.indicators.transforms import log_returns, returns


def add_past_returns(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    df = df.copy()
    if "close" not in df.columns:
        return df

    for p in periods:
        df[f"past_return_{p}"] = returns(df["close"], period=p)

    return df

def add_past_log_returns(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    df = df.copy()
    if "close" not in df.columns:
        return df

    for p in periods:
        df[f"past_log_return_{p}"] = log_returns(df["close"], period=p)

    return df

def add_past_rolling_volatility(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    df = df.copy()
    if "close" not in df.columns:
        return df

    lr = log_returns(df["close"], period=1)
    for p in periods:
        df[f"past_volatility_{p}"] = lr.rolling(window=p, min_periods=p).std()

    return df
