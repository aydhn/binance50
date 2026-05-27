import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.weights import MLBlendWeightEngine

def test_normalize_weights():
    config = AppConfig()
    engine = MLBlendWeightEngine()
    weights = engine.normalize_component_weights(config)
    assert abs(sum(weights.values()) - 1.0) < 1e-6

def test_model_weights():
    config = AppConfig()
    engine = MLBlendWeightEngine()
    w = engine.get_model_weight("logistic_regression", config)
    assert w == 0.35

def test_dummy_weight_zero():
    config = AppConfig()
    engine = MLBlendWeightEngine()
    w = engine.get_model_weight("dummy_classifier", config)
    assert w == 0.0

def test_calibration_penalty():
    config = AppConfig()
    engine = MLBlendWeightEngine()
    w = engine.apply_calibration_penalty(1.0, {"calibrated": False}, config)
    assert w < 1.0

def test_quality_penalty():
    config = AppConfig()
    engine = MLBlendWeightEngine()
    w = engine.apply_quality_penalty(1.0, {"data_quality_issue": True}, config)
    assert w < 1.0
