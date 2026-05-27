import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.probability_blend import compute_weighted_average_probability, compute_probability_blend_confidence, build_probability_blend_component

def test_weighted_probability_average():
    res = compute_weighted_average_probability({"m1": 0.6}, {"m1": 1.0})
    assert "blended_probability" in res

def test_confidence_from_probability():
    conf = compute_probability_blend_confidence(0.8)
    assert abs(conf - 0.6) < 1e-6

def test_component_report():
    comp = build_probability_blend_component(0.8, 0.5, {})
    assert comp.component_name == "ml_probability"
    assert comp.raw_value == 0.8
    assert comp.contribution == 0.4
