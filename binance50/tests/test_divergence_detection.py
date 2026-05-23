import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.indicators.divergence import (
    DivergenceType,
    detect_divergences_for_indicator,
)


def test_divergence_candidates(config: AppConfig):
    # Setup mock dataframe where price makes a lower low, but indicator makes a higher low
    df = pd.DataFrame(
        {
            "close": [10, 8, 12, 10, 6, 12],
            "rsi": [50, 30, 60, 50, 40, 60],  # Price 8->6 (LL), RSI 30->40 (HL) -> Regular Bullish
            "symbol": "BTCUSDT",
            "interval": "1m",
        }
    )

    config.indicator_v2.pivots.left_window = 1
    config.indicator_v2.pivots.min_prominence_pct = 0.0
    config.indicator_v2.divergence.min_price_delta_pct = 0.0
    config.indicator_v2.divergence.min_indicator_delta_pct = 0.0

    cands = detect_divergences_for_indicator(df, "close", "rsi", config)

    bullish = [c for c in cands if c.divergence_type == DivergenceType.regular_bullish]
    assert len(bullish) > 0
    assert bullish[0].score >= 0 and bullish[0].score <= 100


def test_missing_indicator_source(config: AppConfig):
    df = pd.DataFrame(
        {
            "close": [10, 8, 12],
        }
    )
    from binance50.core.exceptions import DivergenceDetectionError

    with pytest.raises(DivergenceDetectionError):
        detect_divergences_for_indicator(df, "close", "missing_rsi", config)
