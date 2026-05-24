import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.divergence_candidate import DivergenceCandidatePlugin


def test_divergence_candidate_plugin():
    config = AppConfig()
    plugin = DivergenceCandidatePlugin()

    df = pd.DataFrame({"open_time": [1000], "div_regular_bullish_score": [80.0]})

    context = build_strategy_context(config, "BTC", "spot", "1m", "divergence")
    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
    assert cands[0].metadata["repainting_risk"]
