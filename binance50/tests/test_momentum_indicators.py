import numpy as np
import pandas as pd
import pytest

from binance50.indicators.momentum import cci, momentum, roc, rsi, stoch_rsi, stochastic, williams_r


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "open": np.random.uniform(10, 20, 100),
        "high": np.random.uniform(20, 25, 100),
        "low": np.random.uniform(5, 10, 100),
        "close": np.random.uniform(10, 20, 100)
    })

def test_rsi(sample_data):
    res = rsi(sample_data["close"], 14)
    assert len(res) == 100
    assert res.name == "mom_rsi_14"
    valid_res = res.dropna()
    assert (valid_res >= 0).all() and (valid_res <= 100).all()

def test_stochastic(sample_data):
    res = stochastic(sample_data["high"], sample_data["low"], sample_data["close"], 14, 3, 3)
    assert len(res) == 100
    assert "mom_stoch_k_14_3_3" in res.columns
    assert "mom_stoch_d_14_3_3" in res.columns

def test_stoch_rsi(sample_data):
    res = stoch_rsi(sample_data["close"], 14, 14, 3, 3)
    assert len(res) == 100
    assert "mom_stoch_rsi_k_14_14_3_3" in res.columns

def test_roc(sample_data):
    res = roc(sample_data["close"], 10)
    assert len(res) == 100
    assert res.name == "mom_roc_10"

def test_momentum(sample_data):
    res = momentum(sample_data["close"], 10)
    assert len(res) == 100
    assert res.name == "mom_mom_10"

def test_cci(sample_data):
    res = cci(sample_data["high"], sample_data["low"], sample_data["close"], 20)
    assert len(res) == 100
    assert res.name == "mom_cci_20"

def test_williams_r(sample_data):
    res = williams_r(sample_data["high"], sample_data["low"], sample_data["close"], 14)
    assert len(res) == 100
    assert res.name == "mom_willr_14"
    valid_res = res.dropna()
    assert (valid_res >= -100).all() and (valid_res <= 0).all()
