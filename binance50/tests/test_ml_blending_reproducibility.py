import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.models import MLBlendingRunResult, MLBlendingRunRequest, MLBlendingStatus
from binance50.ml.blending.reproducibility import compute_blending_output_hash, compute_blending_input_hash, assert_ml_blending_reproducible

def test_hash_deterministic():
    config = AppConfig()
    req1 = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    req2 = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    res1 = MLBlendingRunResult(request=req1, run_id="1", status=MLBlendingStatus.completed)
    res2 = MLBlendingRunResult(request=req2, run_id="1", status=MLBlendingStatus.completed)
    assert compute_blending_output_hash(res1) == compute_blending_output_hash(res2)
    assert_ml_blending_reproducible(res1, res2)

def test_input_hash():
    config = AppConfig()
    inputs1 = {"a": 1}
    inputs2 = {"a": 1}
    assert compute_blending_input_hash(inputs1, config) == compute_blending_input_hash(inputs2, config)
