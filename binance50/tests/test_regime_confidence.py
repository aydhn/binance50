import pandas as pd

from binance50.config.models import AppConfig
from binance50.regimes.confidence import compute_trend_confidence


def test_trend_confidence():
    config = AppConfig()
    config.regimes.features.adx_period = 14
    config.regimes.thresholds.trend_adx_min = 20.0
    config.regimes.thresholds.strong_trend_adx_min = 30.0

    row = pd.Series({"reg_adx_14": 25.0})
    conf = compute_trend_confidence(row, config)
    assert conf == 50.0
