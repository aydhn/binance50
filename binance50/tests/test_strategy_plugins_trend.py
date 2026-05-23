import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.trend_following import TrendFollowingPlugin


def test_trend_following_plugin():
    config = AppConfig()
    plugin = TrendFollowingPlugin()

    df = pd.DataFrame(
        {
            "open_time": [1000],
            "close": [50000],
            "trend_ema_20": [49000],
            "trend_ema_50": [48000],
            "trend_ema_200": [45000],
            "trend_adx_14": [20.0],
        }
    )

    context = build_strategy_context(config, "BTC", "spot", "1m", "trend_following")

    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
    assert cands[0].strength == "medium"
    assert cands[0].intent == "scoring_input"
