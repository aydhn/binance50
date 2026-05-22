import pandas as pd


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    df = pd.concat([tr1, tr2, tr3], axis=1)
    res = df.max(axis=1)
    res.iloc[0] = pd.NA
    return res

from pathlib import Path

file_path = Path("src/binance50/indicators/transforms.py")
content = file_path.read_text()

content = content.replace("""def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    # Concatenate and max along axis 1
    df = pd.concat([tr1, tr2, tr3], axis=1)
    return df.max(axis=1)""", """def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    # Concatenate and max along axis 1
    df = pd.concat([tr1, tr2, tr3], axis=1)
    res = df.max(axis=1)
    if len(res) > 0:
        res.iloc[0] = np.nan
    return res""")

content = content.replace("""def rolling_zscore(series: pd.Series, period: int) -> pd.Series:
    if period <= 1:
        return pd.Series(0.0, index=series.index)

    mean = series.rolling(window=period, min_periods=period).mean()
    std = series.rolling(window=period, min_periods=period).std()

    return safe_divide(series - mean, std)""", """def rolling_zscore(series: pd.Series, period: int) -> pd.Series:
    if period <= 1:
        return pd.Series(0.0, index=series.index)

    mean = series.rolling(window=period, min_periods=period).mean()
    std = series.rolling(window=period, min_periods=period).std()

    # safe_divide replaces nan with 0.0, we want to keep nan where std is nan
    res = safe_divide(series - mean, std)
    res[std.isna()] = np.nan
    return res""")

file_path.write_text(content)
print("Patched transforms")
