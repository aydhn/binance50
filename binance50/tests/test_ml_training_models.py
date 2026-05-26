import pytest
from binance50.ml.training.models import (
    MLTrainingRunRequest,
    MLModelTrainingResult,
    MLTrainingRunResult,
    MLPredictionIntent,
    MLTaskType,
    MLModelType,
    MLModelStatus,
    MLTrainingStatus,
    MLTrainingRunMetadata
)

def test_ml_training_run_request_valid():
    req = MLTrainingRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        dataset_id="ds_123",
        label_column="label_fwd",
        task_type=MLTaskType.classification,
        model_names=["logistic_regression"],
        start_time_ms=1000,
        end_time_ms=2000,
        request_id="req_1",
        correlation_id="corr_1"
    )
    assert req.symbol == "BTCUSDT"

def test_ml_model_training_result_valid():
    res = MLModelTrainingResult(
        model_id="m_1",
        run_id="run_1",
        model_name="lr_1",
        model_type=MLModelType.logistic_regression,
        status=MLModelStatus.trained,
        task_type=MLTaskType.classification,
        started_at_utc="2023",
        finished_at_utc="2024"
    )
    assert res.status == MLModelStatus.trained

def test_ml_prediction_intent():
    assert MLPredictionIntent.research_only == "research_only"
    assert MLPredictionIntent.no_order == "no_order"
    assert MLPredictionIntent.no_live == "no_live"
    assert MLPredictionIntent.no_paper == "no_paper"
