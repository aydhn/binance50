import pytest
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.inference.predictor import MLBatchPredictor
from binance50.ml.inference.models import MLPredictionRow, MLInferenceIntent
from binance50.core.exceptions import MLPredictionError

class MockEstimator:
    def predict(self, X):
        return np.array([1, 0])

    def predict_proba(self, X):
        return np.array([[0.1, 0.9], [0.8, 0.2]])

class MockModelResult:
    run_id = "test"

def test_batch_iter():
    config = AppConfig()
    pred = MLBatchPredictor(config)
    X = pd.DataFrame({"f1": [1, 2, 3, 4, 5]})

    batches = list(pred.batch_iter(X, 2))
    assert len(batches) == 3
    assert len(batches[0][0]) == 2
    assert len(batches[2][0]) == 1

def test_predict_batch():
    config = AppConfig()
    pred = MLBatchPredictor(config)
    X = pd.DataFrame({"f1": [1, 2]})
    row_meta = [{"index": 0}, {"index": 1}]

    rows = pred.predict_batch(MockEstimator(), X, row_meta, MockModelResult(), config)

    assert len(rows) == 2
    assert rows[0].predicted_label == "1"
    assert rows[0].max_probability == 0.9
    assert rows[1].predicted_label == "0"
    assert rows[1].max_probability == 0.8
    assert rows[0].prediction_intent == MLInferenceIntent.RESEARCH_ONLY

def test_validate_predictions():
    config = AppConfig()
    pred = MLBatchPredictor(config)

    row = MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label="1", predicted_class_index=1, feature_schema_hash="h"
    )

    pred.validate_predictions([row], config)

    with pytest.raises(MLPredictionError, match="No predictions"):
        pred.validate_predictions([], config)

    row.prediction_intent = "live"
    with pytest.raises(MLPredictionError, match="Invalid prediction intent"):
        pred.validate_predictions([row], config)
