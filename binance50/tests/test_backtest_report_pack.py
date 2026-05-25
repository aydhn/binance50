from binance50.backtest.analytics.report_pack import BacktestReportPackBuilder
from binance50.config.models import AppConfig


class MockResult:
    def __init__(self):
        self.run_id = "test_run_123"
        self.strategy_name = "test_strat"
        self.symbols = ["BTCUSDT"]
        self.initial_capital = 1000.0
        self.input_hash = "abc"
        self.config_hash = "def"


def test_backtest_report_pack_builder():
    config = AppConfig()
    result = MockResult()

    builder = BacktestReportPackBuilder(config)
    pack = builder.build(result)

    assert pack.run_id == "test_run_123"
    assert pack.report_id == "rep_test_run_123"
    assert "DISCLAIMER" in pack.disclaimer
    assert pack.input_hash == "abc"
    assert pack.config_hash == "def"
    assert pack.report_hash != ""
    assert pack.quality is not None


def test_compute_report_hash_deterministic():
    config = AppConfig()
    result = MockResult()

    builder = BacktestReportPackBuilder(config)
    pack1 = builder.build(result)
    pack2 = builder.build(result)

    assert pack1.report_hash == pack2.report_hash
