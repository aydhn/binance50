import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.regime_policy import compute_regime_blend_component, apply_transition_or_unknown_penalty

class MockRegime:
    regime_type = "trend"

def test_compute_regime_blend_component():
    config = AppConfig()
    comp = compute_regime_blend_component(MockRegime(), 1, config)
    assert comp.component_name == "regime_context"

def test_unknown_penalty():
    config = AppConfig()
    class MockUnknown:
        regime_type = "unknown"
    pen = apply_transition_or_unknown_penalty(MockUnknown(), config)
    assert pen == config.ml_blending.weights.penalties.unknown_regime_penalty

def test_transition_penalty():
    config = AppConfig()
    class MockTransition:
        regime_type = "transition"
    pen = apply_transition_or_unknown_penalty(MockTransition(), config)
    assert pen == config.ml_blending.weights.penalties.transition_regime_penalty
