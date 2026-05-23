import numpy as np
import pandas as pd
import pytest

from binance50.indicators.volatility import (
    atr,
    bollinger_bands,
    bollinger_bandwidth,
    donchian_channels,
    keltner_channels,
    natr,
    realized_volatility,
    rolling_std,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "open": np.random.uniform(10, 20, 100),
            "high": np.random.uniform(20, 25, 100),
            "low": np.random.uniform(5, 10, 100),
            "close": np.random.uniform(10, 20, 100),
        }
    )


def test_atr(sample_data):
    res = atr(sample_data["high"], sample_data["low"], sample_data["close"], 14)
    assert len(res) == 100
    assert res.name == "vol_atr_14"
    valid_res = res.dropna()
    assert (valid_res >= 0).all()


def test_natr(sample_data):
    res = natr(sample_data["high"], sample_data["low"], sample_data["close"], 14)
    assert len(res) == 100
    assert res.name == "vol_natr_14"
    valid_res = res.dropna()
    assert (valid_res >= 0).all()


def test_bollinger_bands(sample_data):
    res = bollinger_bands(sample_data["close"], 20, 2.0)
    assert len(res) == 100
    assert "vol_bb_mid_20_2" in res.columns
    assert "vol_bb_upper_20_2" in res.columns
    assert "vol_bb_lower_20_2" in res.columns
    valid_res = res.dropna()
    assert (valid_res["vol_bb_upper_20_2"] >= valid_res["vol_bb_mid_20_2"]).all()
    assert (valid_res["vol_bb_mid_20_2"] >= valid_res["vol_bb_lower_20_2"]).all()


def test_bollinger_bandwidth(sample_data):
    res = bollinger_bandwidth(sample_data["close"], 20, 2.0)
    assert len(res) == 100
    assert res.name == "vol_bb_width_20_2"
    valid_res = res.dropna()
    assert (valid_res >= 0).all()


def test_keltner_channels(sample_data):
    res = keltner_channels(
        sample_data["high"], sample_data["low"], sample_data["close"], 20, 14, 2.0
    )
    assert len(res) == 100
    assert "vol_kc_mid_20_14_2" in res.columns
    assert "vol_kc_upper_20_14_2" in res.columns
    assert "vol_kc_lower_20_14_2" in res.columns
    valid_res = res.dropna()
    assert (valid_res["vol_kc_upper_20_14_2"] >= valid_res["vol_kc_mid_20_14_2"]).all()
    assert (valid_res["vol_kc_mid_20_14_2"] >= valid_res["vol_kc_lower_20_14_2"]).all()


def test_donchian_channels(sample_data):
    res = donchian_channels(sample_data["high"], sample_data["low"], 20)
    assert len(res) == 100
    assert "vol_donchian_high_20" in res.columns
    assert "vol_donchian_low_20" in res.columns


def test_rolling_std(sample_data):
    res = rolling_std(sample_data["close"], 20)
    assert len(res) == 100
    assert res.name == "vol_rolling_std_20"
    valid_res = res.dropna()
    assert (valid_res >= 0).all()


def test_realized_volatility(sample_data):
    res = realized_volatility(sample_data["close"], 20)
    assert len(res) == 100
    assert res.name == "vol_realized_20"
