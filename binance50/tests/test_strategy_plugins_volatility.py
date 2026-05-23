import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.volatility_breakout import VolatilityBreakoutPlugin


def test_volatility_breakout_plugin():
    config = AppConfig()
    plugin = VolatilityBreakoutPlugin()

    df = pd.DataFrame(
        {
            "open_time": [1000],
            "close": [51000],
            "vol_atr_14": [100.0],
            "vol_donchian_high_20": [50000],
            "vol_donchian_low_20": [40000],
        }
    )

    context = build_strategy_context(config, "BTC", "spot", "1m", "volatility_breakout")
    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
