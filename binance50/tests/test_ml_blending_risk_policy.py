import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.risk_policy import compute_risk_blend_component, apply_high_risk_penalty

class MockRisk:
    risk_level = "high"

def test_compute_risk_blend_component():
    config = AppConfig()
    comp = compute_risk_blend_component(MockRisk(), config)
    assert comp.component_name == "risk_context"

def test_high_risk_penalty():
    config = AppConfig()
    pen = apply_high_risk_penalty(MockRisk(), config)
    assert pen == config.ml_blending.weights.penalties.high_risk_context_penalty
