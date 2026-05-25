import pandas as pd

from binance50.backtest.analytics.regime_breakdown import (
    assign_regime_to_trades,
    build_regime_breakdown_table,
    compute_metrics_by_regime,
    validate_regime_breakdown,
)
from binance50.config.models import AppConfig


class MockTrade:
    def __init__(self, entry_time, pnl):
        self.entry_time = entry_time
        self.pnl_usdt = pnl


def test_assign_regime_to_trades():
    idx = pd.date_range("2023-01-01", periods=3)
    regimes = pd.Series(["bull", "bear", "range"], index=idx)

    trades = [
        MockTrade(idx[0], 10),
        MockTrade(idx[1], -5),
        MockTrade(pd.Timestamp("2024-01-01"), 20),
    ]
    assigned = assign_regime_to_trades(trades, regimes)

    assert assigned[0]["regime"] == "bull"
    assert assigned[1]["regime"] == "bear"
    assert assigned[2]["regime"] == "unknown"


def test_compute_metrics_by_regime():
    idx = pd.date_range("2023-01-01", periods=2)
    regimes = pd.Series(["bull", "bull"], index=idx)
    trades = [MockTrade(idx[0], 10), MockTrade(idx[1], -5)]
    assigned = assign_regime_to_trades(trades, regimes)

    metrics = compute_metrics_by_regime(assigned)
    assert "bull" in metrics
    assert metrics["bull"]["count"] == 2
    assert metrics["bull"]["total_pnl"] == 5.0
    assert metrics["bull"]["win_rate"] == 0.5
    assert metrics["bull"]["payoff_ratio"] == 2.0


def test_validate_regime_breakdown():
    config = AppConfig()
    config.backtest_reporting.breakdowns.min_trades_per_bucket_warning = 3

    metrics = {"bull": {"count": 2}}
    warnings = validate_regime_breakdown(metrics, config)
    assert len(warnings) == 1


def test_build_regime_breakdown_table():
    metrics = {"bull": {"count": 2, "total_pnl": 5.0}}
    table = build_regime_breakdown_table(metrics)
    assert table[0]["regime"] == "bull"
    assert table[0]["count"] == 2
