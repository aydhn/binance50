import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.mean_reversion import MeanReversionPlugin


def test_mean_reversion_plugin():
    config = AppConfig()
    plugin = MeanReversionPlugin()

    df = pd.DataFrame(
        {
            "open_time": [1000],
            "close": [40000],
            "mom_rsi_14": [25.0],
            "vol_bb_lower_20_2": [41000],
            "vol_bb_upper_20_2": [45000],
        }
    )

    context = build_strategy_context(config, "BTC", "spot", "1m", "mean_reversion")

    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
    assert "mean reversion candidate" in cands[0].explanation.summary.lower()
