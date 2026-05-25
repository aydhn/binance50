import pandas as pd
import pytest

from binance50.backtest.analytics.drawdown_v2 import (
    compute_average_drawdown,
    compute_drawdown_duration,
    compute_recovery_time,
    compute_underwater_curve,
    detect_top_drawdowns,
)


def test_compute_underwater_curve():
    eq = pd.Series([100, 110, 105, 120, 90, 100])
    uw = compute_underwater_curve(eq)
    assert uw.iloc[0] == 0.0
    assert uw.iloc[1] == 0.0
    assert uw.iloc[2] < 0.0  # 105/110 - 1
    assert uw.iloc[3] == 0.0
    assert uw.iloc[4] < 0.0  # 90/120 - 1


def test_detect_top_drawdowns():
    # Make sure index has datetimes
    idx = pd.date_range("2023-01-01", periods=6)
    eq = pd.Series([100, 110, 105, 120, 90, 100], index=idx)
    dds = detect_top_drawdowns(eq, 2)
    assert len(dds) == 2
    assert dds[0]["depth"] == pytest.approx(-0.25)  # 90/120 - 1


def test_compute_average_drawdown():
    dds = [{"depth": -0.1}, {"depth": -0.2}]
    avg = compute_average_drawdown(dds)
    assert avg == pytest.approx(-0.15)


def test_compute_drawdown_duration():
    # Placeholder test
    assert compute_drawdown_duration(pd.Series()) == {}


def test_compute_recovery_time():
    assert compute_recovery_time({"recovered": False}) is None
    assert compute_recovery_time({"recovered": True}) is None  # Placeholder
