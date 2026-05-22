import numpy as np
import pandas as pd
import pytest

from binance50.indicators.trend import (
    adx,
    aroon,
    dema,
    ema,
    ma_slope,
    macd,
    price_above_ma,
    sma,
    tema,
    wma,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "open": np.random.uniform(10, 20, 100),
        "high": np.random.uniform(20, 25, 100),
        "low": np.random.uniform(5, 10, 100),
        "close": np.random.uniform(10, 20, 100)
    })

def test_sma(sample_data):
    res = sma(sample_data["close"], 10)
    assert len(res) == 100
    assert pd.isna(res.iloc[8])
    assert not pd.isna(res.iloc[9])

def test_ema(sample_data):
    res = ema(sample_data["close"], 10)
    assert len(res) == 100
    assert pd.isna(res.iloc[8])
    assert not pd.isna(res.iloc[9])

def test_wma(sample_data):
    res = wma(sample_data["close"], 10)
    assert len(res) == 100
    assert pd.isna(res.iloc[8])
    assert not pd.isna(res.iloc[9])

def test_dema(sample_data):
    res = dema(sample_data["close"], 10)
    assert len(res) == 100
    assert pd.isna(res.iloc[8]) # Note: dema min_periods behavior might delay first valid depending on implementation, but ema keeps it at 10.

def test_tema(sample_data):
    res = tema(sample_data["close"], 10)
    assert len(res) == 100

def test_macd(sample_data):
    res = macd(sample_data["close"], 12, 26, 9)
    assert len(res) == 100
    assert "trend_macd_12_26_9" in res.columns
    assert "trend_macd_signal_12_26_9" in res.columns
    assert "trend_macd_hist_12_26_9" in res.columns

def test_adx(sample_data):
    res = adx(sample_data["high"], sample_data["low"], sample_data["close"], 14)
    assert len(res) == 100
    assert "trend_adx_14" in res.columns
    assert "trend_plus_di_14" in res.columns
    assert "trend_minus_di_14" in res.columns

def test_aroon(sample_data):
    res = aroon(sample_data["high"], sample_data["low"], 14)
    assert len(res) == 100
    assert "trend_aroon_up_14" in res.columns
    assert "trend_aroon_down_14" in res.columns
    assert "trend_aroon_osc_14" in res.columns
    assert pd.isna(res["trend_aroon_up_14"].iloc[13])
    assert not pd.isna(res["trend_aroon_up_14"].iloc[14])

def test_price_above_ma(sample_data):
    ma = sma(sample_data["close"], 10)
    res = price_above_ma(sample_data["close"], ma)
    assert len(res) == 100

def test_ma_slope(sample_data):
    ma = sma(sample_data["close"], 10)
    res = ma_slope(ma, 2)
    assert len(res) == 100
    assert pd.isna(res.iloc[10]) # ma valid at 9, shifted 2 -> valid at 11
    assert not pd.isna(res.iloc[11])
