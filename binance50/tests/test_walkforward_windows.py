import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.windows import (
    apply_window_limits,
    build_anchored_expanding_windows,
    build_expanding_windows,
    build_rolling_windows,
)


def test_rolling_windows():
    config = AppConfig()
    df = pd.DataFrame({"a": range(4000)})
    windows = build_rolling_windows(df, config)
    assert len(windows) > 0
    assert windows[0].train_rows == config.walkforward.windows.train_bars
    assert windows[0].validation_rows == config.walkforward.windows.validation_bars


def test_expanding_windows():
    config = AppConfig()
    df = pd.DataFrame({"a": range(4000)})
    windows = build_expanding_windows(df, config)
    assert len(windows) > 0


def test_anchored_expanding_windows():
    config = AppConfig()
    df = pd.DataFrame({"a": range(4000)})
    windows = build_anchored_expanding_windows(df, config)
    assert len(windows) > 0
    assert windows[0].train_start == 0


def test_window_limits():
    config = AppConfig()
    config.walkforward.mode.max_windows = 2
    df = pd.DataFrame({"a": range(10000)})
    windows = build_rolling_windows(df, config)
    limited = apply_window_limits(windows, config)
    assert len(limited) == 2
