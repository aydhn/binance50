import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.reproducibility import (
    compute_ml_training_input_hash, compute_model_config_hash,
    compute_training_run_hash, compute_model_result_hash,
    assert_ml_training_reproducible
)

class MockResult:
    run_id = "1"
    model_id = "1"

def test_reproducibility():
    config = AppConfig()
    h1 = compute_ml_training_input_hash({"a": 1}, config)
    assert h1

    h2 = compute_model_config_hash("logistic_regression", config)
    assert h2

    r1 = MockResult()
    r2 = MockResult()

    assert compute_training_run_hash(r1) == compute_training_run_hash(r2)
    assert_ml_training_reproducible(r1, r2)
