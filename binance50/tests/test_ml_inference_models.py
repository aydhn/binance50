import pytest
from binance50.ml.inference.models import (
    MLInferenceStatus,
    MLInferenceMode,
    MLInferenceIntent,
    MLPredictionOutputType,
    MLSandboxOutputStatus,
    MLInferenceRunRequest,
    MLModelLoadReport,
    MLPredictionRow,
    MLInferenceManifest,
    MLInferenceRunResult,
)

def test_ml_inference_enums():
    assert MLInferenceStatus.PENDING == "pending"
    assert MLInferenceMode.OFFLINE_BATCH == "offline_batch"
    assert MLInferenceIntent.RESEARCH_ONLY == "research_only"
    assert MLPredictionOutputType.CLASS_LABEL == "class_label"
    assert MLSandboxOutputStatus.SANDBOX_ONLY == "sandbox_only"

def test_ml_inference_run_request():
    req = MLInferenceRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        model_id="test_model",
        dataset_id="test_dataset",
        split_name="test",
        start_time_ms=1000,
        end_time_ms=2000,
        request_id="req_1",
        correlation_id="corr_1",
    )
    assert req.symbol == "BTCUSDT"

def test_ml_model_load_report():
    report = MLModelLoadReport(
        model_id="test_model",
        artifact_id="art_1",
        trusted_artifact=True,
        artifact_hash_expected="hash1",
        artifact_hash_actual="hash1",
        hash_verified=True,
        environment_match=True,
        model_card_present=True,
        dataset_manifest_link_present=True,
        feature_schema_hash="schema_hash",
        loaded_at_utc="now",
    )
    assert report.hash_verified is True

def test_ml_prediction_row():
    row = MLPredictionRow(
        prediction_id="pred_1",
        model_id="test_model",
        dataset_id="test_dataset",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time="now",
        predicted_label="up",
        predicted_class_index=1,
        feature_schema_hash="schema_hash",
    )
    assert row.prediction_intent == MLInferenceIntent.RESEARCH_ONLY
    assert not hasattr(row, 'order_id')
    assert not hasattr(row, 'quantity')

def test_ml_inference_manifest():
    manifest = MLInferenceManifest(
        inference_id="inf_1",
        run_id="run_1",
        model_id="test_model",
        artifact_id="art_1",
        dataset_id="test_dataset",
        split_name="test",
        row_count=100,
        prediction_count=100,
        feature_schema_hash="schema_hash",
        model_hash="model_hash",
        dataset_hash="ds_hash",
        preprocessor_hash="prep_hash",
        config_hash="cfg_hash",
        output_hash="out_hash",
        calibration_status="calibrated",
        created_at_utc="now",
    )
    assert manifest.feature_schema_hash == "schema_hash"

def test_ml_inference_run_result():
    req = MLInferenceRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        model_id="test_model",
        dataset_id="test_dataset",
        split_name="test",
        start_time_ms=1000,
        end_time_ms=2000,
        request_id="req_1",
        correlation_id="corr_1",
    )
    res = MLInferenceRunResult(
        request=req,
        run_id="run_1",
        status=MLInferenceStatus.COMPLETED,
        success=True,
    )
    assert res.success is True
