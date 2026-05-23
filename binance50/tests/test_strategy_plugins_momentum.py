import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.momentum_continuation import MomentumContinuationPlugin


def test_momentum_continuation_plugin():
    config = AppConfig()
    plugin = MomentumContinuationPlugin()

    df = pd.DataFrame(
        {
            "open_time": [1000],
            "mom_rsi_14": [60.0],
            "trend_macd_hist_12_26_9": [1.5],
            "mom_roc_10": [2.0],
        }
    )

    context = build_strategy_context(config, "BTC", "spot", "1m", "momentum_continuation")

    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
    assert cands[0].confidence > 50.0
