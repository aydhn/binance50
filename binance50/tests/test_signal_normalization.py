import pytest
import math
from binance50.config.models import AppConfig
from binance50.signals.normalization import (
    clamp_score, normalize_confidence, normalize_plugin_weight,
    normalize_component, score_to_tier, safe_weighted_value
)
from binance50.core.exceptions import SignalValidationError

@pytest.fixture
def config():
    return AppConfig()

def test_clamp_score():
    assert clamp_score(50.0) == 50.0
    assert clamp_score(-10.0) == 0.0
    assert clamp_score(150.0) == 100.0

    with pytest.raises(SignalValidationError):
        clamp_score(float('nan'))

    with pytest.raises(SignalValidationError):
        clamp_score(float('inf'))

def test_normalize_confidence(config):
    assert normalize_confidence(50.0, config) == 50.0
    assert normalize_confidence(150.0, config) == 100.0

def test_normalize_plugin_weight():
    assert normalize_plugin_weight(1.5) == 1.5
    assert normalize_plugin_weight(-1.0) == 0.0

def test_normalize_component():
    assert normalize_component(50, 0, 100) == 50.0
    assert normalize_component(200, 0, 100) == 100.0
    assert normalize_component(-50, 0, 100) == 0.0
    assert normalize_component(float('nan'), 0, 100) == 0.0

def test_score_to_tier(config):
    assert score_to_tier(10.0, config).value == "very_low"
    assert score_to_tier(30.0, config).value == "low"
    assert score_to_tier(50.0, config).value == "medium"
    assert score_to_tier(70.0, config).value == "high"
    assert score_to_tier(90.0, config).value == "very_high"

def test_safe_weighted_value():
    assert safe_weighted_value(50.0, 0.5) == 25.0
    assert safe_weighted_value(float('nan'), 0.5) == 0.0
    assert safe_weighted_value(50.0, float('inf')) == 0.0
