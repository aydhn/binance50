import pandas as pd
import pytest

from binance50.backtest.analytics.periodic_returns import (
    build_calendar_heatmap_table,
    build_monthly_return_matrix,
    compute_daily_returns,
    compute_monthly_returns,
    compute_quarterly_returns,
    compute_weekly_returns,
    compute_yearly_returns,
    summarize_periodic_returns,
)
from binance50.core.exceptions import BacktestPeriodicReturnError


def _make_equity():
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    equity = pd.Series(range(100, 200), index=dates, dtype=float)
    return equity


def test_compute_daily_returns():
    eq = _make_equity()
    ret = compute_daily_returns(eq)
    assert not ret.empty


def test_datetime_index_required():
    eq = pd.Series([100, 110, 120])
    with pytest.raises(BacktestPeriodicReturnError):
        compute_daily_returns(eq)


def test_compute_weekly_returns():
    eq = _make_equity()
    ret = compute_weekly_returns(eq)
    assert not ret.empty


def test_compute_monthly_returns():
    eq = _make_equity()
    ret = compute_monthly_returns(eq)
    assert not ret.empty


def test_compute_quarterly_returns():
    eq = _make_equity()
    ret = compute_quarterly_returns(eq)
    assert not ret.empty


def test_compute_yearly_returns():
    eq = _make_equity()
    ret = compute_yearly_returns(eq)
    assert not ret.empty


def test_build_monthly_matrix():
    eq = _make_equity()
    ret = compute_monthly_returns(eq)
    matrix = build_monthly_return_matrix(ret)
    assert not matrix.empty
    assert "YTD" in matrix.columns


def test_calendar_heatmap_table():
    eq = _make_equity()
    ret = compute_monthly_returns(eq)
    table = build_calendar_heatmap_table(ret)
    assert len(table) > 0
    assert "year" in table[0]


def test_summarize_periodic_returns():
    eq = _make_equity()
    ret = compute_monthly_returns(eq)
    summary = summarize_periodic_returns(ret)
    assert "best_period" in summary
    assert "worst_period" in summary
