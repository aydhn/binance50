import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_training_guard import (
    assert_ml_training_config_safe, assert_no_prediction_serving,
    assert_no_execution_integration, assert_no_live_paper_intent
)

class MockPayload:
    prediction_intent = "live"

def test_ml_training_guard():
    config = AppConfig()

    assert_ml_training_config_safe(config)

    config.ml_training.real_exchange_forbidden = False
    with pytest.raises(ValueError, match="real_exchange_forbidden"):
        assert_ml_training_config_safe(config)

    config = AppConfig()
    config.ml_training.prediction_serving_deferred = False
    with pytest.raises(ValueError, match="Prediction serving"):
        assert_no_prediction_serving(config)

    with pytest.raises(ValueError, match="Live/paper intent found"):
        assert_no_live_paper_intent(MockPayload())
