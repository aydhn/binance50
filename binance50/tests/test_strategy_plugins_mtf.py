import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.mtf_confirmation import MTFConfirmationPlugin


def test_mtf_confirmation_plugin():
    config = AppConfig()
    plugin = MTFConfirmationPlugin()

    df = pd.DataFrame({"open_time": [1000], "mtf_1h_mom_rsi_14": [70.0]})

    context = build_strategy_context(config, "BTC", "spot", "1m", "mtf")
    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
    assert cands[0].metadata["future_leakage_guard_passed"]
