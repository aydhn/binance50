import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardMode, WalkForwardWindow
from binance50.walkforward.oos import classify_oos_window_quality, run_oos_backtest_for_window


def test_oos_run():
    config = AppConfig()
    window = WalkForwardWindow(
        window_id="w1",
        index=0,
        mode=WalkForwardMode.rolling_window,
        train_start=0,
        train_end=1,
        validation_start=1,
        validation_end=2,
        test_start=2,
        test_end=3,
        train_rows=1,
        validation_rows=1,
        test_rows=1,
        embargo_bars=0,
    )
    bt, rp = run_oos_backtest_for_window(window, {}, pd.DataFrame(), None, None, None, config)
    assert classify_oos_window_quality(rp, config) in ["good", "poor"]
