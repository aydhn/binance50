import pandas as pd

from binance50.config.models import AppConfig
from binance50.indicators.feature_metadata import build_feature_metadata_for_columns


def test_feature_metadata_builder(config: AppConfig):
    config.indicator_v2.feature_groups.enabled = True
    config.indicator_v2.feature_groups.groups = {
        "trend": {"prefixes": ["trend_"]},
        "divergence": {"prefixes": ["div_"]},
        "patterns": {"prefixes": ["pat_"]},
    }
    df = pd.DataFrame(
        {
            "open_time": [1, 2, 3],
            "trend_ema_20": [10.0, 11.0, 12.0],
            "div_regular_bullish_rsi_14_flag": [False, True, False],
            "pat_doji_skeleton": [0, 50, 0],
        }
    )

    metadata = build_feature_metadata_for_columns(df, config)

    assert len(metadata) == 3

    trend = next(m for m in metadata if m.feature_name == "trend_ema_20")
    assert trend.group == "trend"
    assert not trend.is_divergence
    assert not trend.is_pattern

    div = next(m for m in metadata if m.feature_name == "div_regular_bullish_rsi_14_flag")
    assert div.group == "divergence"
    assert div.is_divergence

    pat = next(m for m in metadata if m.feature_name == "pat_doji_skeleton")
    assert pat.group == "patterns"
    assert pat.is_pattern
