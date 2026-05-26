import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.trainer import MLTrainer
from binance50.ml.training.dataset_loader import MLTrainingDatasetLoader
from binance50.ml.training.estimators import MLEstimatorFactory
from binance50.ml.training.validation import MLTimeSeriesValidationEngine
from binance50.ml.training.registry import MLModelRegistry
from binance50.ml.training.models import MLTrainingRunRequest, MLTaskType

def test_ml_trainer():
    config = AppConfig()
    loader = MLTrainingDatasetLoader()
    factory = MLEstimatorFactory()
    val = MLTimeSeriesValidationEngine()
    reg = MLModelRegistry(config)

    trainer = MLTrainer(config, loader, factory, val, reg)

    req = MLTrainingRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m", dataset_id="ds1",
        label_column="label", task_type=MLTaskType.classification,
        model_names=["logistic_regression"], start_time_ms=0, end_time_ms=10,
        request_id="req1", correlation_id="c1"
    )

    res = trainer.run(req)
    assert res.success is True
    assert len(res.model_results) == 1
    assert res.model_results[0].status.value == "trained"

    assert reg.get_model(res.model_results[0].model_id) is not None
