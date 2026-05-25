from binance50.config.models import AppConfig
from binance50.optimizer.adapters.optuna_adapter import OptunaAdapter
from binance50.optimizer.models import OptimizationRunRequest


def test_optuna_missing_graceful():
    adapter = OptunaAdapter()
    assert adapter.name == "optuna"


def test_fail_if_missing_false():
    adapter = OptunaAdapter()
    config = AppConfig()
    req = OptimizationRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        method="optuna_optional",
        request_id="1",
    )

    # We force Optuna missing
    adapter._available = False
    config.optimizer.optuna_optional.fail_if_missing = False

    result = adapter.run(req, [], None, config)
    assert not result.success
    assert result.error == "Optuna is not installed"


def test_availability_report():
    adapter = OptunaAdapter()
    rep = adapter.availability_report()
    assert "name" in rep
    assert "available" in rep
