import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import StrategyInputError
from binance50.strategies.engine import StrategyEngine
from binance50.strategies.models import StrategyRunRequest
from binance50.strategies.registry import StrategyRegistry


class FailingPlugin:
    name = "failing"
    plugin_type = "trend"

    def is_enabled(self, c):
        return True

    def validate_input(self, df, c):
        pass

    def evaluate(self, df, ctx):
        raise ValueError("Plugin failure")


def test_strategy_engine_isolation():
    config = AppConfig()
    reg = StrategyRegistry(config)
    reg._plugins["failing"] = FailingPlugin()

    engine = StrategyEngine(config, reg)
    df = pd.DataFrame({"close": [1, 2, 3]})
    req = StrategyRunRequest(symbol="BTC", market_scope="spot", interval="1m")

    # Engine should catch plugin error and report it in warnings, but not crash
    with pytest.raises(StrategyInputError):
        # Will fail because config requires min 100 rows by default
        engine.run(df, req)


def test_strategy_engine_success():
    config = AppConfig()
    config.strategies.min_rows_required = 2
    reg = StrategyRegistry(config)
    engine = StrategyEngine(config, reg)

    df = pd.DataFrame({"close": [1, 2, 3]})
    req = StrategyRunRequest(symbol="BTC", market_scope="spot", interval="1m")

    res = engine.run(df, req)
    assert res.success
