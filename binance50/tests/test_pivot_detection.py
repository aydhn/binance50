import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.indicators.pivots import detect_causal_pivot_highs, detect_causal_pivot_lows, PivotType, detect_price_pivots
from binance50.core.exceptions import PivotDetectionError

def test_causal_pivot_high(config: AppConfig):
    series = pd.Series([10, 11, 12, 10, 9, 8, 13, 14, 15, 12, 11])
    # 12 is a pivot high (idx 2)
    # 15 is a pivot high (idx 8)

    pivots = detect_causal_pivot_highs(series, left_window=2, min_prominence_pct=0.01, min_distance_bars=2)
    assert len(pivots) == 2
    assert pivots[0].index == 2
    assert pivots[1].index == 8

def test_causal_pivot_low(config: AppConfig):
    series = pd.Series([10, 9, 8, 10, 11, 12, 7, 6, 5, 8, 9])

    pivots = detect_causal_pivot_lows(series, left_window=2, min_prominence_pct=0.01, min_distance_bars=2)
    assert len(pivots) == 2
    assert pivots[0].index == 2
    assert pivots[1].index == 8

def test_min_distance(config: AppConfig):
    # Multiple highs close to each other
    series = pd.Series([10, 15, 14, 16, 10, 9])

    # 15 and 16 are highs, but with distance 2 they should both trigger if causal,
    # but wait, 14 is lower than 15, so 15 is a causal peak.
    # 16 is higher than 15, so 16 is a causal peak.

    # Let's just use detect_price_pivots which enforces the distance
    df = pd.DataFrame({"close": series, "symbol": "BTCUSDT", "interval": "1m"})
    config.indicator_v2.pivots.min_distance_bars = 5
    config.indicator_v2.pivots.left_window = 1

    pivots = detect_price_pivots(df, "close", config)
    # Due to distance, only one high should remain
    highs = [p for p in pivots if p.pivot_type == PivotType.high]
    assert len(highs) <= 1

def test_repainting_config_throws(config: AppConfig):
    with pytest.raises(ValueError):
        from binance50.config.models import PivotConfig
        PivotConfig(allow_repainting=True)
