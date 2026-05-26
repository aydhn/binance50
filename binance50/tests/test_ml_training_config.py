import pytest
from pydantic import ValidationError
from binance50.config.models import MLTrainingConfig, MLTrainingDatasetConfig

def test_ml_training_config_default_safe():
    config = MLTrainingConfig()
    assert config.real_exchange_forbidden is True
    assert config.paper_trade_forbidden is True
    assert config.live_trade_forbidden is True
    assert config.order_creation_forbidden is True
    assert config.api_key_forbidden is True
    assert config.signed_request_forbidden is True
    assert config.dashboard_forbidden is True
    assert config.prediction_serving_deferred is True
    assert config.execution_integration_forbidden is True
    assert config.auto_strategy_update_forbidden is True
    assert config.registry.active_model_serving_forbidden is True
    assert config.registry.auto_promote_forbidden is True

def test_ml_training_config_live_trade_error():
    with pytest.raises(ValidationError, match="live_trade_forbidden must be True"):
        MLTrainingConfig(live_trade_forbidden=False)

def test_ml_training_config_prediction_serving_error():
    with pytest.raises(ValidationError, match="prediction_serving_deferred must be True"):
        MLTrainingConfig(prediction_serving_deferred=False)

def test_ml_training_config_dataset_requirements():
    with pytest.raises(ValidationError, match="require_leakage_free_dataset must be True"):
        MLTrainingConfig(dataset=MLTrainingDatasetConfig(require_leakage_free_dataset=False))
