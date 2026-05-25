from binance50.backtest.analytics.holding_time import (
    compute_avg_holding_bars,
    compute_holding_time_distribution,
    compute_median_holding_bars,
    compute_pnl_by_holding_bucket,
)


class MockTrade:
    def __init__(self, pnl, bars):
        self.pnl_usdt = pnl
        self.holding_bars = bars


def test_compute_avg_holding_bars():
    trades = [MockTrade(10, 2), MockTrade(-5, 4)]
    assert compute_avg_holding_bars(trades) == 3.0
    assert compute_avg_holding_bars([]) is None


def test_compute_median_holding_bars():
    trades = [MockTrade(10, 2), MockTrade(-5, 10), MockTrade(20, 4)]
    assert compute_median_holding_bars(trades) == 4.0


def test_compute_holding_time_distribution():
    trades = [MockTrade(10, 1), MockTrade(-5, 3), MockTrade(20, 15), MockTrade(0, 150)]
    dist = compute_holding_time_distribution(trades)
    assert dist["1 bar"] == 1
    assert dist["2-5 bars"] == 1
    assert dist["6-20 bars"] == 1
    assert dist["100+ bars"] == 1


def test_compute_pnl_by_holding_bucket():
    trades = [MockTrade(10, 1), MockTrade(-5, 3), MockTrade(20, 15)]
    pnl = compute_pnl_by_holding_bucket(trades)
    assert pnl["1 bar"] == 10.0
    assert pnl["2-5 bars"] == -5.0
    assert pnl["6-20 bars"] == 20.0
