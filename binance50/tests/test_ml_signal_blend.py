import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.signal_blend import normalize_signal_score_to_probability, map_signal_direction_to_class, compute_signal_component, compute_signal_model_agreement, apply_signal_conflict_penalty

class MockSignal:
    score = 80.0
    direction = 1

def test_normalize_signal_score():
    config = AppConfig()
    norm = normalize_signal_score_to_probability(80.0, config)
    assert abs(norm - 0.8) < 1e-6

def test_direction_mapping():
    assert map_signal_direction_to_class(1) == 1
    assert map_signal_direction_to_class(-1) == 0

def test_signal_component():
    config = AppConfig()
    comp = compute_signal_component(MockSignal(), config)
    assert comp.component_name == "rule_signal"
    assert comp.raw_value == 80.0
    assert abs(comp.normalized_value - 0.8) < 1e-6

def test_signal_model_agreement():
    config = AppConfig()
    res = compute_signal_model_agreement(MockSignal(), {}, config)
    assert res["agreement"] is True

def test_conflict_penalty():
    config = AppConfig()
    comp = apply_signal_conflict_penalty(MockSignal(), config)
    assert comp.penalty == config.ml_blending.weights.penalties.signal_model_disagreement_penalty
