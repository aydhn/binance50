import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.safety.feature_guard import assert_feature_dataframe_safe
from binance50.core.exceptions import FeatureQualityError

def test_target_column_rejected(config: AppConfig):
    df = pd.DataFrame({"target_buy": [1, 0, 1]})
    with pytest.raises(FeatureQualityError, match="Prohibited target/future columns found"):
        assert_feature_dataframe_safe(df, config)

def test_future_return_rejected(config: AppConfig):
    df = pd.DataFrame({"future_return_5m": [0.01, -0.01]})
    with pytest.raises(FeatureQualityError, match="Prohibited target/future columns found"):
        assert_feature_dataframe_safe(df, config)

def test_secret_rejected(config: AppConfig):
    df = pd.DataFrame({"api_key_str": ["x", "y"]})
    with pytest.raises(FeatureQualityError, match="Secret-like column name detected"):
        assert_feature_dataframe_safe(df, config)

def test_safe_dataframe(config: AppConfig):
    df = pd.DataFrame({"trend_ema_20": [1, 2, 3], "mom_rsi": [50, 60, 40]})
    # Should not raise
    assert_feature_dataframe_safe(df, config)
