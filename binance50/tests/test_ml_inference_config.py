from binance50.config.models import AppConfig
import pytest


def test_ml_inference_config_defaults():
    config = AppConfig()

    assert config.ml_inference.enabled is True
    assert config.ml_inference.prediction.mode == "offline_batch"
    assert config.ml_inference.prediction.prediction_intent == "research_only"

def test_ml_inference_config_safety_enforcement():
    config = AppConfig()

    # Try breaking safety rules
    with pytest.raises(ValueError, match="real_exchange_forbidden must be True"):
        config.ml_inference.real_exchange_forbidden = False
        config.ml_inference.validate_safety_flags()

    with pytest.raises(ValueError, match="prediction_serving_forbidden must be True"):
        config.ml_inference.real_exchange_forbidden = True
        config.ml_inference.prediction_serving_forbidden = False
        config.ml_inference.validate_safety_flags()

def test_ml_inference_config_threshold_validation():
    config = AppConfig()

    # Try invalid thresholds
    with pytest.raises(ValueError, match="threshold values must be between 0 and 1"):
        config.ml_inference.threshold_sweep.thresholds = [1.5]
        config.ml_inference.validate_safety_flags()

def test_ml_inference_config_probability_validation():
    config = AppConfig()

    with pytest.raises(ValueError, match="probability min/max must be between 0 and 1"):
        config.ml_inference.probability.max_probability = 1.1
        config.ml_inference.validate_safety_flags()
