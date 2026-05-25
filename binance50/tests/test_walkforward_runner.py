from binance50.config.models import AppConfig
from binance50.walkforward.runner import WalkForwardRunner


def test_walkforward_runner_fixture():
    config = AppConfig()
    runner = WalkForwardRunner(config)
    res = runner.run_from_fixture("mock", "BTCUSDT", "spot", "1m")
    assert res.success
    assert len(res.windows) > 0
    assert len(res.window_results) > 0
