from binance50.backtest.analytics.exposure_analysis import (
    build_exposure_report,
    compute_turnover_from_trades,
)
from binance50.config.models import AppConfig


class MockTrade:
    def __init__(self, price, qty):
        self.entry_price = price
        self.quantity = qty


class MockResult:
    def __init__(self, trades):
        self.trades = trades


def test_compute_turnover_from_trades():
    trades = [MockTrade(100, 2), MockTrade(50, 10)]
    # turnover = (100*2*2) + (50*10*2) = 400 + 1000 = 1400
    assert compute_turnover_from_trades(trades) == 1400.0


def test_build_exposure_report():
    config = AppConfig()
    trades = [MockTrade(100, 2), MockTrade(50, 10)]
    res = MockResult(trades)

    report = build_exposure_report(res, config)
    assert report["turnover_notional"] == 1400.0
    assert "simulation_note" in report["metadata"]
