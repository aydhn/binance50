import numpy as np
import pandas as pd
import pytest

from binance50.indicators.transforms import (
    hl_range,
    log_returns,
    median_price,
    oc_change,
    returns,
    rolling_zscore,
    safe_divide,
    true_range,
    typical_price,
    weighted_close,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "open": [10, 11, 12, 11, 10],
        "high": [12, 13, 14, 13, 12],
        "low": [9, 10, 11, 10, 9],
        "close": [11, 12, 11, 10, 11]
    })

def test_typical_price(sample_data):
    tp = typical_price(sample_data["high"], sample_data["low"], sample_data["close"])
    assert tp.iloc[0] == pytest.approx((12 + 9 + 11) / 3.0)

def test_median_price(sample_data):
    mp = median_price(sample_data["high"], sample_data["low"])
    assert mp.iloc[0] == pytest.approx((12 + 9) / 2.0)

def test_weighted_close(sample_data):
    wc = weighted_close(sample_data["high"], sample_data["low"], sample_data["close"])
    assert wc.iloc[0] == pytest.approx((12 + 9 + (11 * 2)) / 4.0)

def test_hl_range(sample_data):
    hl = hl_range(sample_data["high"], sample_data["low"])
    assert hl.iloc[0] == pytest.approx(12 - 9)

def test_oc_change(sample_data):
    oc = oc_change(sample_data["open"], sample_data["close"])
    assert oc.iloc[0] == pytest.approx(11 - 10)

def test_true_range(sample_data):
    tr = true_range(sample_data["high"], sample_data["low"], sample_data["close"])
    assert pd.isna(tr.iloc[0]) # No previous close
    # High is 13, Low is 10, Prev Close is 11
    # max(13-10, |13-11|, |10-11|) = max(3, 2, 1) = 3
    assert tr.iloc[1] == 3.0

def test_returns(sample_data):
    ret = returns(sample_data["close"], period=1)
    assert pd.isna(ret.iloc[0])
    assert ret.iloc[1] == pytest.approx((12 - 11) / 11.0)

    with pytest.raises(ValueError):
        returns(sample_data["close"], period=-1)

def test_log_returns(sample_data):
    # Add a zero/negative close to test safety
    data = sample_data.copy()
    data.loc[2, "close"] = 0
    data.loc[3, "close"] = -1

    log_ret = log_returns(data["close"], period=1)
    assert pd.isna(log_ret.iloc[0])
    assert log_ret.iloc[1] == pytest.approx(np.log(12 / 11.0))
    assert pd.isna(log_ret.iloc[2]) # prev zero
    assert pd.isna(log_ret.iloc[3]) # neg

    with pytest.raises(ValueError):
        log_returns(sample_data["close"], period=0)

def test_safe_divide():
    num = pd.Series([10, 20, 30])
    den = pd.Series([2, 0, 5])

    res = safe_divide(num, den)
    assert res.iloc[0] == 5.0
    assert res.iloc[1] == 0.0 # Handled divide by zero
    assert res.iloc[2] == 6.0

def test_rolling_zscore():
    series = pd.Series([1, 2, 3, 4, 5])
    z = rolling_zscore(series, 3)
    assert pd.isna(z.iloc[0])
    assert pd.isna(z.iloc[1])
    assert z.iloc[2] == pytest.approx((3 - 2) / 1.0) # Mean of 1,2,3 is 2, std is 1
