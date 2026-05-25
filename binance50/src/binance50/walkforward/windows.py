import hashlib
import json

import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardMode, WalkForwardWindow, WalkForwardWindowStatus


def build_walkforward_windows(df: pd.DataFrame, config: AppConfig) -> list[WalkForwardWindow]:
    wf_config = config.walkforward
    mode_str = wf_config.mode.default_mode
    mode = WalkForwardMode(mode_str)

    if mode == WalkForwardMode.rolling_window:
        windows = build_rolling_windows(df, config)
    elif mode == WalkForwardMode.expanding_window:
        windows = build_expanding_windows(df, config)
    elif mode == WalkForwardMode.anchored_expanding:
        windows = build_anchored_expanding_windows(df, config)
    else:
        raise ValueError(f"Unsupported walkforward mode: {mode}")

    windows = apply_window_limits(windows, config)
    validate_window_order(windows)
    return windows


def build_rolling_windows(df: pd.DataFrame, config: AppConfig) -> list[WalkForwardWindow]:
    wf_config = config.walkforward
    train_bars = wf_config.windows.train_bars
    validation_bars = wf_config.windows.validation_bars
    test_bars = wf_config.windows.test_bars
    step_bars = wf_config.windows.step_bars

    total_len = len(df)
    windows: list[WalkForwardWindow] = []

    window_size = train_bars + validation_bars + test_bars
    if total_len < window_size:
        return windows

    start_idx = 0
    idx = 0
    while start_idx + window_size <= total_len:
        train_start = start_idx
        train_end = train_start + train_bars
        val_start = train_end
        val_end = val_start + validation_bars
        test_start = val_end
        test_end = test_start + test_bars

        window = WalkForwardWindow(
            window_id=f"win_{idx:03d}",
            index=idx,
            mode=WalkForwardMode.rolling_window,
            train_start=train_start,
            train_end=train_end,
            validation_start=val_start,
            validation_end=val_end,
            test_start=test_start,
            test_end=test_end,
            train_rows=train_bars,
            validation_rows=validation_bars,
            test_rows=test_bars,
            embargo_bars=wf_config.windows.embargo_bars,
            status=WalkForwardWindowStatus.pending,
        )
        windows.append(window)
        start_idx += step_bars
        idx += 1

    return windows


def build_expanding_windows(df: pd.DataFrame, config: AppConfig) -> list[WalkForwardWindow]:
    wf_config = config.walkforward
    initial_train_bars = wf_config.expanding.initial_train_bars
    val_bars = wf_config.windows.validation_bars
    test_bars = wf_config.windows.test_bars
    step_bars = wf_config.expanding.train_expansion_step_bars

    total_len = len(df)
    windows: list[WalkForwardWindow] = []

    idx = 0
    train_bars = initial_train_bars
    while train_bars + val_bars + test_bars <= total_len:
        train_start = (
            0 if wf_config.expanding.anchored_start else (train_bars - initial_train_bars)
        )  # Approximate
        train_end = train_bars
        val_start = train_end
        val_end = val_start + val_bars
        test_start = val_end
        test_end = test_start + test_bars

        window = WalkForwardWindow(
            window_id=f"win_{idx:03d}",
            index=idx,
            mode=WalkForwardMode.expanding_window,
            train_start=train_start,
            train_end=train_end,
            validation_start=val_start,
            validation_end=val_end,
            test_start=test_start,
            test_end=test_end,
            train_rows=train_end - train_start,
            validation_rows=val_bars,
            test_rows=test_bars,
            embargo_bars=wf_config.windows.embargo_bars,
            status=WalkForwardWindowStatus.pending,
        )
        windows.append(window)
        train_bars += step_bars
        idx += 1

    return windows


def build_anchored_expanding_windows(
    df: pd.DataFrame, config: AppConfig
) -> list[WalkForwardWindow]:
    wf_config = config.walkforward
    initial_train_bars = wf_config.expanding.initial_train_bars
    val_bars = wf_config.windows.validation_bars
    test_bars = wf_config.windows.test_bars
    step_bars = wf_config.expanding.train_expansion_step_bars

    total_len = len(df)
    windows: list[WalkForwardWindow] = []

    idx = 0
    train_end = initial_train_bars
    while train_end + val_bars + test_bars <= total_len:
        train_start = 0
        val_start = train_end
        val_end = val_start + val_bars
        test_start = val_end
        test_end = test_start + test_bars

        window = WalkForwardWindow(
            window_id=f"win_{idx:03d}",
            index=idx,
            mode=WalkForwardMode.anchored_expanding,
            train_start=train_start,
            train_end=train_end,
            validation_start=val_start,
            validation_end=val_end,
            test_start=test_start,
            test_end=test_end,
            train_rows=train_end - train_start,
            validation_rows=val_bars,
            test_rows=test_bars,
            embargo_bars=wf_config.windows.embargo_bars,
            status=WalkForwardWindowStatus.pending,
        )
        windows.append(window)
        train_end += step_bars
        idx += 1

    return windows


def apply_window_limits(
    windows: list[WalkForwardWindow], config: AppConfig
) -> list[WalkForwardWindow]:
    max_windows = config.walkforward.mode.max_windows
    if len(windows) > max_windows:
        return windows[:max_windows]
    return windows


def validate_window_order(windows: list[WalkForwardWindow]) -> None:
    for w in windows:
        assert w.train_start < w.train_end, "Train start must be before train end"
        assert w.train_end <= w.validation_start, "Validation start must be >= train end"
        assert w.validation_start < w.validation_end, (
            "Validation start must be before validation end"
        )
        assert w.validation_end <= w.test_start, "Test start must be >= validation end"
        assert w.test_start < w.test_end, "Test start must be before test end"


def compute_window_plan_hash(windows: list[WalkForwardWindow]) -> str:
    plan_data = []
    for w in windows:
        plan_data.append(
            {
                "train_start": w.train_start,
                "train_end": w.train_end,
                "validation_start": w.validation_start,
                "validation_end": w.validation_end,
                "test_start": w.test_start,
                "test_end": w.test_end,
            }
        )
    plan_str = json.dumps(plan_data, sort_keys=True)
    return hashlib.sha256(plan_str.encode("utf-8")).hexdigest()


def windows_to_dataframe(windows: list[WalkForwardWindow]) -> pd.DataFrame:
    data = [w.model_dump() for w in windows]
    return pd.DataFrame(data)
