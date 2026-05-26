import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.dataset_loader import MLTrainingDatasetLoader, MLDatasetBuildResult

def test_dataset_loader_validation():
    config = AppConfig()
    loader = MLTrainingDatasetLoader()

    # Missing leakage status
    with pytest.raises(ValueError, match="Dataset is not leakage free"):
        result = MLDatasetBuildResult({"dataset_id": "test"}, None)
        loader.validate_dataset_for_training(result, config)

    # Missing quality status
    with pytest.raises(ValueError, match="Dataset failed quality checks"):
        result = MLDatasetBuildResult({"dataset_id": "test", "leakage_status": "clean"}, None)
        loader.validate_dataset_for_training(result, config)

    # Valid
    result = MLDatasetBuildResult({"dataset_id": "test", "leakage_status": "clean", "quality_status": "passed"}, None)
    loader.validate_dataset_for_training(result, config)
