import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.quality import (
    build_ml_training_quality_report, assert_ml_training_quality_passed
)
from binance50.ml.training.models import MLModelTrainingResult, MLModelStatus, MLTaskType

class MockResult:
    run_id = "run1"
    dataset_manifest = {"id": "1"}
    model_results = []

def test_ml_training_quality():
    config = AppConfig()
    res = MockResult()

    # No models
    rep = build_ml_training_quality_report(res, config)
    assert rep.status == "failed"
    assert rep.missing_dataset_manifest_count == 0
    with pytest.raises(ValueError, match="No models"):
        assert_ml_training_quality_passed(rep, config)

    # With missing metrics
    m1 = MLModelTrainingResult(
        model_id="m1", run_id="r1", model_name="name", model_type="dummy_classifier",
        status=MLModelStatus.trained, task_type=MLTaskType.classification,
        started_at_utc="utc", finished_at_utc="utc"
    )
    res.model_results = [m1]
    rep2 = build_ml_training_quality_report(res, config)
    assert rep2.missing_metrics_count == 1
    with pytest.raises(ValueError, match="Missing metrics"):
        assert_ml_training_quality_passed(rep2, config)
