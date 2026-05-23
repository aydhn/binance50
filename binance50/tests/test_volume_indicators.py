import numpy as np
import pandas as pd
import pytest

from binance50.indicators.volume import (
    accumulation_distribution_line,
    cmf,
    mfi,
    obv,
    volume_ema,
    volume_rate_of_change,
    volume_sma,
    vwap,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "open": np.random.uniform(10, 20, 100),
            "high": np.random.uniform(20, 25, 100),
            "low": np.random.uniform(5, 10, 100),
            "close": np.random.uniform(10, 20, 100),
            "volume": np.random.uniform(100, 1000, 100),
        }
    )


def test_obv(sample_data):
    res = obv(sample_data["close"], sample_data["volume"])
    assert len(res) == 100
    assert res.name == "volu_obv"


def test_volume_sma(sample_data):
    res = volume_sma(sample_data["volume"], 20)
    assert len(res) == 100
    assert res.name == "volu_volume_sma_20"


def test_volume_ema(sample_data):
    res = volume_ema(sample_data["volume"], 20)
    assert len(res) == 100
    assert res.name == "volu_volume_ema_20"


def test_vwap(sample_data):
    res = vwap(
        sample_data["high"], sample_data["low"], sample_data["close"], sample_data["volume"], 20
    )
    assert len(res) == 100
    assert res.name == "volu_vwap_20"


def test_mfi(sample_data):
    res = mfi(
        sample_data["high"], sample_data["low"], sample_data["close"], sample_data["volume"], 14
    )
    assert len(res) == 100
    assert res.name == "volu_mfi_14"
    valid_res = res.dropna()
    assert (valid_res >= 0).all() and (valid_res <= 100).all()


def test_cmf(sample_data):
    res = cmf(
        sample_data["high"], sample_data["low"], sample_data["close"], sample_data["volume"], 20
    )
    assert len(res) == 100
    assert res.name == "volu_cmf_20"
    valid_res = res.dropna()
    assert (valid_res >= -1).all() and (valid_res <= 1).all()


def test_adl(sample_data):
    res = accumulation_distribution_line(
        sample_data["high"], sample_data["low"], sample_data["close"], sample_data["volume"]
    )
    assert len(res) == 100
    assert res.name == "volu_adl"


def test_volume_rate_of_change(sample_data):
    res = volume_rate_of_change(sample_data["volume"], 10)
    assert len(res) == 100
    assert res.name == "volu_vroc_10"
