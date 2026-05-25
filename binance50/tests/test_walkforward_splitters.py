import pandas as pd

from binance50.walkforward.models import WalkForwardMode, WalkForwardWindow
from binance50.walkforward.splitters import (
    assert_no_split_overlap,
    slice_window_data,
)


def test_slice_window_data():
    df = pd.DataFrame({"a": range(4000)})
    window = WalkForwardWindow(
        window_id="test",
        index=0,
        mode=WalkForwardMode.rolling_window,
        train_start=0,
        train_end=1000,
        validation_start=1000,
        validation_end=1200,
        test_start=1200,
        test_end=1400,
        train_rows=1000,
        validation_rows=200,
        test_rows=200,
        embargo_bars=0,
    )
    t, v, te = slice_window_data(df, window)
    assert len(t) == 1000
    assert len(v) == 200
    assert len(te) == 200


def test_assert_no_split_overlap():
    t = pd.DataFrame({"open_time": [1, 2, 3]})
    v = pd.DataFrame({"open_time": [4, 5, 6]})
    te = pd.DataFrame({"open_time": [7, 8, 9]})
    assert_no_split_overlap(t, v, te)
