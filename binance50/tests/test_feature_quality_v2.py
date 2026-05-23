import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.indicators.quality_v2 import build_feature_quality_report
from binance50.indicators.feature_registry import FeatureRegistry
from binance50.core.exceptions import FeatureQualityError
import numpy as np

def test_feature_quality(config: AppConfig):
    reg = FeatureRegistry(config)

    df = pd.DataFrame({
        "open_time": [1, 2, 3],
        "trend_ema": [10.0, 11.0, np.nan],
        "mom_rsi": [50.0, 60.0, 70.0],
        "future_price": [10, 20, 30] # Target keyword
    })

    rep = build_feature_quality_report(df, ["trend_ema", "mom_rsi", "future_price"], config, reg)
    assert rep.status == "fail"

    issues = [i.issue_type for i in rep.issues]
    assert "lookahead" in issues
    assert "ungrouped" in issues # future_price has no group
    assert "unregistered" in issues # none are registered

def test_all_nan(config: AppConfig):
    df = pd.DataFrame({
        "trend_ema": [np.nan, np.nan, np.nan]
    })
    rep = build_feature_quality_report(df, ["trend_ema"], config)
    issues = [i.issue_type for i in rep.issues]
    assert "all_nan" in issues

def test_inf(config: AppConfig):
    df = pd.DataFrame({
        "trend_ema": [1.0, np.inf, 2.0]
    })
    rep = build_feature_quality_report(df, ["trend_ema"], config)
    issues = [i.issue_type for i in rep.issues]
    assert "inf_values" in issues
