import pytest

from binance50.backtest.analytics.trade_distribution import (
    compute_best_worst_trades,
    compute_consecutive_wins_losses,
    compute_trade_pnl_percentiles,
    compute_trade_return_histogram,
    compute_trade_return_percentiles,
    compute_win_loss_distribution,
)


class MockTrade:
    def __init__(self, pnl, ret=0.0):
        self.pnl_usdt = pnl
        self.return_pct = ret
        self.id = "mock"


def test_compute_win_loss_distribution():
    trades = [MockTrade(10), MockTrade(-5), MockTrade(20)]
    dist = compute_win_loss_distribution(trades)
    assert dist["total_trades"] == 3
    assert dist["wins"] == 2
    assert dist["losses"] == 1


def test_compute_trade_return_histogram():
    trades = [MockTrade(10, 0.05), MockTrade(-5, -0.02)]
    hist = compute_trade_return_histogram(trades, 10)
    assert "counts" in hist
    assert "edges" in hist


def test_compute_best_worst_trades():
    trades = [MockTrade(10), MockTrade(-5), MockTrade(20), MockTrade(-15)]
    bw = compute_best_worst_trades(trades, 1)
    assert bw["best"][0]["pnl"] == 20
    assert bw["worst"][0]["pnl"] == -15


def test_compute_consecutive_wins_losses():
    trades = [MockTrade(10), MockTrade(20), MockTrade(-5), MockTrade(-10), MockTrade(-15)]
    cons = compute_consecutive_wins_losses(trades)
    assert cons["max_consecutive_wins"] == 2
    assert cons["max_consecutive_losses"] == 3


def test_percentiles():
    trades = [MockTrade(i) for i in range(1, 101)]
    pnl_p = compute_trade_pnl_percentiles(trades)
    ret_p = compute_trade_return_percentiles(trades)
    assert pnl_p["p50"] == pytest.approx(50.5)
    assert ret_p["p50"] == pytest.approx(0.0)
