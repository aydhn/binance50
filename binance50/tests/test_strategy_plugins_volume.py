import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import build_strategy_context
from binance50.strategies.plugins.volume_confirmation import VolumeConfirmationPlugin


def test_volume_confirmation_plugin():
    config = AppConfig()
    plugin = VolumeConfirmationPlugin()

    df = pd.DataFrame(
        {
            "open_time": [1000, 2000],
            "volume": [100, 1500],
            "volu_volume_sma_20": [1000, 1000],
            "volu_obv": [5000, 6000],  # Increase = bullish
        }
    )

    context = build_strategy_context(config, "BTC", "spot", "1m", "volume_confirmation")
    cands = plugin.evaluate(df, context)
    assert len(cands) == 1
    assert cands[0].direction == "bullish"
