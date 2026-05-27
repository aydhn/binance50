import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_blending_threshold_guard import assert_thresholds_research_only, assert_no_execution_threshold
from binance50.core.exceptions import MLBlendingThresholdError

def test_thresholds_research_only():
    config = AppConfig()
    assert_thresholds_research_only(config)

def test_no_execution_threshold():
    config = AppConfig()
    assert_no_execution_threshold(config)
