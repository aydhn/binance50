import numpy as np
import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeLeakageError
from binance50.regimes.features import build_regime_features, validate_regime_feature_frame


def test_build_features_no_lookahead():
    config = AppConfig()
    df = pd.DataFrame(
        {
            "close": np.linspace(100, 200, 50),
            "ADX": np.linspace(10, 40, 50),
            "upper_bb": np.linspace(110, 210, 50),
            "lower_bb": np.linspace(90, 190, 50),
            "mid_bb": np.linspace(100, 200, 50),
            "volume": np.linspace(1000, 2000, 50),
        }
    )
    feat = build_regime_features(df, config)
    assert f"reg_trend_slope_{config.regimes.features.trend_windows[0]}" in feat.columns
    assert f"reg_realized_vol_{config.regimes.features.volatility_windows[0]}" in feat.columns
    assert f"reg_bb_width_pct_{config.regimes.features.bb_width_period}" in feat.columns


def test_leakage_detected():
    config = AppConfig()
    df = pd.DataFrame({"close": [100, 110], "future_return": [0.1, -0.1]})
    with pytest.raises(RegimeLeakageError):
        validate_regime_feature_frame(df, config)
