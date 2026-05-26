import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.registry import MLModelRegistry
from binance50.ml.training.models import MLTrainingRunResult, MLModelTrainingResult

class MockRunResult:
    run_id = "run1"
    dataset_manifest = {}
    best_validation_model = "m1"

class MockModelResult:
    model_id = "m1"
    model_card = None

def test_ml_model_registry():
    config = AppConfig()
    registry = MLModelRegistry(config)

    run = MockRunResult()
    with pytest.raises(ValueError, match="Training manifest required"):
        registry.register_training_run(run)

    run.dataset_manifest = {"id": "1"}
    registry.register_training_run(run)
    assert len(registry.runs) == 1

    model = MockModelResult()
    with pytest.raises(ValueError, match="Model card required"):
        registry.register_model(model)

    model.model_card = {"id": "1"}
    registry.register_model(model)
    assert registry.get_model("m1") == model

    with pytest.raises(RuntimeError, match="forbidden"):
        registry.promote_model_for_serving("m1")
