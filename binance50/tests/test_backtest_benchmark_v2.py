import pandas as pd
import pytest

from binance50.backtest.analytics.benchmark_v2 import (
    align_strategy_and_benchmark,
    compute_alpha_beta_placeholder,
    compute_buy_and_hold_equity,
    compute_excess_return,
    compute_information_ratio,
    compute_tracking_error,
    validate_benchmark_date_range,
)
from binance50.config.models import AppConfig
from binance50.core.exceptions import BacktestBenchmarkV2Error


def test_compute_buy_and_hold():
    config = AppConfig()
    ohlcv = pd.DataFrame({"close": [100, 110, 105]}, index=pd.date_range("2023-01-01", periods=3))
    equity = compute_buy_and_hold_equity(ohlcv, 1000, config)
    assert equity.iloc[0] == 1000
    assert equity.iloc[1] == 1100
    assert equity.iloc[2] == 1050


def test_align_strategy_and_benchmark():
    idx1 = pd.date_range("2023-01-01", periods=5)
    idx2 = pd.date_range("2023-01-03", periods=5)
    s1 = pd.Series([1, 2, 3, 4, 5], index=idx1)
    s2 = pd.Series([3, 4, 5, 6, 7], index=idx2)

    a1, a2 = align_strategy_and_benchmark(s1, s2)
    assert len(a1) == 3
    assert len(a2) == 3


def test_compute_excess_return():
    s1 = pd.Series([0.05, 0.02])
    s2 = pd.Series([0.02, 0.01])
    exc = compute_excess_return(s1, s2)
    assert exc.iloc[0] == pytest.approx(0.03)
    assert exc.iloc[1] == 0.01


def test_compute_tracking_error():
    s1 = pd.Series([0.05, 0.02, -0.01])
    s2 = pd.Series([0.02, 0.01, -0.02])
    te = compute_tracking_error(s1, s2, 365)
    assert te is not None


def test_compute_information_ratio():
    exc = pd.Series([0.03, 0.01, 0.01])
    ir = compute_information_ratio(exc, 365)
    assert ir is not None


def test_compute_alpha_beta_placeholder():
    s1 = pd.Series([0.05, 0.02, -0.01])
    s2 = pd.Series([0.02, 0.01, -0.02])
    alpha, beta = compute_alpha_beta_placeholder(s1, s2)
    assert alpha is not None
    assert beta is not None


def test_validate_benchmark_date_range():
    config = AppConfig()
    idx1 = pd.date_range("2023-01-01", periods=5)
    idx2 = pd.date_range("2023-01-03", periods=5)
    s1 = pd.Series([1] * 5, index=idx1)
    s2 = pd.Series([1] * 5, index=idx2)

    with pytest.raises(BacktestBenchmarkV2Error):
        validate_benchmark_date_range(s1, s2, config)
