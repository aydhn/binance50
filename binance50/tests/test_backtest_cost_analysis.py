import pytest

from binance50.backtest.analytics.cost_analysis import (
    build_cost_impact_report,
    compute_cost_drag_pct,
    compute_cost_per_trade,
    compute_gross_vs_net_pnl,
    compute_total_fee_cost,
    compute_total_slippage_cost,
)
from binance50.config.models import AppConfig


class MockTrade:
    def __init__(self, pnl, fee, slippage):
        self.pnl_usdt = pnl
        self.fee_usdt = fee
        self.slippage_usdt = slippage


class MockResult:
    def __init__(self, trades):
        self.trades = trades


def test_compute_total_fee_cost():
    trades = [MockTrade(10, 1, 0.5), MockTrade(-5, 0.5, 0.2)]
    assert compute_total_fee_cost(trades) == 1.5


def test_compute_total_slippage_cost():
    trades = [MockTrade(10, 1, 0.5), MockTrade(-5, 0.5, 0.2)]
    assert compute_total_slippage_cost(trades) == 0.7


def test_compute_gross_vs_net_pnl():
    trades = [MockTrade(10, 1, 0.5), MockTrade(-5, 0.5, 0.2)]
    # net = 10 - 5 = 5
    # gross = 5 + 1.5 + 0.7 = 7.2
    gross, net = compute_gross_vs_net_pnl(trades)
    assert gross == pytest.approx(7.2)
    assert net == pytest.approx(5.0)


def test_compute_cost_drag_pct():
    assert compute_cost_drag_pct(100, 90) == 10.0
    assert compute_cost_drag_pct(-10, -20) is None  # gross <= 0


def test_compute_cost_per_trade():
    trades = [MockTrade(10, 1, 0.5), MockTrade(-5, 0.5, 0.2)]
    # total costs = 2.2 / 2 = 1.1
    assert compute_cost_per_trade(trades) == pytest.approx(1.1)


def test_build_cost_impact_report():
    config = AppConfig()
    config.backtest_reporting.costs.high_cost_drag_pct = 10.0

    trades = [MockTrade(10, 1, 0.5), MockTrade(-5, 0.5, 0.2)]
    res = MockResult(trades)

    report = build_cost_impact_report(res, config)
    assert report["gross_pnl"] == pytest.approx(7.2)
    assert report["net_pnl"] == pytest.approx(5.0)
    assert len(report["warnings"]) == 1  # 30.5% drag > 10%
