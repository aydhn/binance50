import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLInferenceRunResult, MLInferenceRunRequest, MLInferenceStatus, MLModelLoadReport, MLPredictionRow
from binance50.ml.inference.quality import build_ml_inference_quality_report, assert_ml_inference_quality_passed
from binance50.core.exceptions import MLInferenceQualityError

def test_quality_report_passed():
    config = AppConfig()
    req = MLInferenceRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", model_id="m1", dataset_id="d1", split_name="test", start_time_ms=0, end_time_ms=1, request_id="r1", correlation_id="c1")

    rep = MLModelLoadReport(model_id="m1", artifact_id="a1", trusted_artifact=True, artifact_hash_expected="h", artifact_hash_actual="h", hash_verified=True, environment_match=True, model_card_present=True, dataset_manifest_link_present=True, feature_schema_hash="h", loaded_at_utc="now")

    preds = [MLPredictionRow(prediction_id="p1", model_id="m1", dataset_id="d1", symbol="BTC", market_scope="spot", interval="1m", open_time="now", predicted_label="1", predicted_class_index=1, feature_schema_hash="h")]

    res = MLInferenceRunResult(request=req, run_id="r1", status=MLInferenceStatus.COMPLETED, success=True, model_load_report=rep, predictions=preds)

    q_rep = build_ml_inference_quality_report(res, config)
    assert q_rep.status == "passed"
    assert_ml_inference_quality_passed(q_rep, config)

def test_quality_report_failed():
    config = AppConfig()
    req = MLInferenceRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", model_id="m1", dataset_id="d1", split_name="test", start_time_ms=0, end_time_ms=1, request_id="r1", correlation_id="c1")

    res = MLInferenceRunResult(request=req, run_id="r1", status=MLInferenceStatus.COMPLETED, success=True) # missing model load report and preds

    q_rep = build_ml_inference_quality_report(res, config)
    assert q_rep.status == "failed"
    assert q_rep.no_model_loaded_count == 1
    assert q_rep.missing_prediction_count == 1

    with pytest.raises(MLInferenceQualityError, match="Quality checks failed"):
        assert_ml_inference_quality_passed(q_rep, config)
