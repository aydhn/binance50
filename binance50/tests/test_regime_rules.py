import pandas as pd

from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime
from binance50.regimes.rules import detect_range_rule, detect_trend_down_rule, detect_trend_up_rule


def test_trend_up_rule():
    config = AppConfig()
    row = pd.Series(
        {
            f"reg_adx_{config.regimes.features.adx_period}": 30.0,
            f"reg_trend_slope_{config.regimes.features.slope_window}": 0.001,
        }
    )
    decision = detect_trend_up_rule(row, config)
    assert decision is not None
    assert decision.regime == MarketRegime.trend_up


def test_trend_down_rule():
    config = AppConfig()
    row = pd.Series(
        {
            f"reg_adx_{config.regimes.features.adx_period}": 30.0,
            f"reg_trend_slope_{config.regimes.features.slope_window}": -0.001,
        }
    )
    decision = detect_trend_down_rule(row, config)
    assert decision is not None
    assert decision.regime == MarketRegime.trend_down


def test_range_rule():
    config = AppConfig()
    row = pd.Series({f"reg_adx_{config.regimes.features.adx_period}": 15.0})
    decision = detect_range_rule(row, config)
    assert decision is not None
    assert decision.regime == MarketRegime.range_bound
