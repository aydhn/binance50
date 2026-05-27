import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow, MLInferenceRunResult, MLInferenceRunRequest, MLInferenceStatus
from binance50.ml.inference.reproducibility import (
    compute_ml_inference_input_hash,
    compute_prediction_hash,
    compute_inference_output_hash,
    compute_inference_config_hash,
    build_ml_inference_reproducibility_report
)

def build_pred(pid, label="1"):
    return MLPredictionRow(
        prediction_id=pid, model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h"
    )

def test_hashes_deterministic():
    config = AppConfig()
    preds1 = [build_pred("1", "0")]
    preds2 = [build_pred("1", "0")]

    req = MLInferenceRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m", model_id="m1", dataset_id="d1",
        split_name="test", start_time_ms=0, end_time_ms=1, request_id="r1", correlation_id="c1"
    )
    res = MLInferenceRunResult(request=req, run_id="r1", status=MLInferenceStatus.COMPLETED, success=True, predictions=preds1)

    assert compute_prediction_hash(preds1) == compute_prediction_hash(preds2)
    assert compute_inference_config_hash(config) == compute_inference_config_hash(config)
    assert compute_inference_output_hash(res) == compute_inference_output_hash(res)

def test_reproducibility_report():
    config = AppConfig()
    req = MLInferenceRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m", model_id="m1", dataset_id="d1",
        split_name="test", start_time_ms=0, end_time_ms=1, request_id="r1", correlation_id="c1"
    )
    res = MLInferenceRunResult(request=req, run_id="r1", status=MLInferenceStatus.COMPLETED, success=True)

    rep = build_ml_inference_reproducibility_report(res, config)
    assert "input_hash" in rep
    assert "output_hash" in rep
    assert "config_hash" in rep
