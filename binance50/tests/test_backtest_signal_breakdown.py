from binance50.backtest.analytics.signal_breakdown import (
    analyze_performance_by_direction,
    analyze_performance_by_strategy_plugin,
    build_score_bucket_table,
)
from binance50.config.models import AppConfig


class MockTrade:
    def __init__(self, pnl, signal, risk, plugin, direction):
        self.pnl_usdt = pnl
        self.signal_score = signal
        self.risk_score = risk
        self.strategy_plugin = plugin
        self.direction = direction


def test_build_score_bucket_table():
    trades = [MockTrade(10, 30, 0, "", ""), MockTrade(-5, 45, 0, "", "")]
    table = build_score_bucket_table(trades, "signal_score")
    # should have multiple buckets
    assert len(table) == 2
    assert table[0]["bucket"] == "0-40"
    assert table[1]["bucket"] == "40-50"


def test_analyze_performance_by_strategy_plugin():
    config = AppConfig()
    trades = [MockTrade(10, 0, 0, "plugin_a", ""), MockTrade(-5, 0, 0, "plugin_b", "")]
    res = analyze_performance_by_strategy_plugin(trades, config)
    assert len(res["table"]) == 2
    assert res["table"][0]["plugin"] == "plugin_a"


def test_analyze_performance_by_direction():
    config = AppConfig()
    trades = [MockTrade(10, 0, 0, "", "LONG"), MockTrade(-5, 0, 0, "", "SHORT")]
    res = analyze_performance_by_direction(trades, config)
    assert len(res["table"]) == 2
    assert res["table"][0]["direction"] == "LONG"
    assert res["table"][1]["direction"] == "SHORT"
