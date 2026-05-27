import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.calibration_policy import compute_calibration_quality_component, compute_brier_penalty, compute_ece_penalty

def test_compute_calibration_quality_component():
    config = AppConfig()
    comp = compute_calibration_quality_component({}, config)
    assert comp.component_name == "calibration_quality"
    assert comp.weight == config.ml_blending.weights.components.calibration_quality_weight

def test_compute_brier_penalty():
    config = AppConfig()
    pen = compute_brier_penalty({"brier_score": 0.3}, config)
    assert pen == config.ml_blending.weights.penalties.high_brier_penalty

def test_compute_ece_penalty():
    config = AppConfig()
    pen = compute_ece_penalty({"ece": 0.2}, config)
    assert pen == config.ml_blending.weights.penalties.high_ece_penalty
