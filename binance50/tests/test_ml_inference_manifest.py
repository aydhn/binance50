import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.manifest import build_inference_manifest, manifest_to_report

def build_pred(prob, label="1"):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob
    )

def test_build_inference_manifest():
    config = AppConfig()
    preds = [build_pred(0.8)]
    ctx = {
        "model_id": "m1",
        "run_id": "r1",
        "model_hash": "mh",
    }

    class MockCalRep:
        calibration_status = "verified"

    reports = {"calibration": MockCalRep()}

    manifest = build_inference_manifest(ctx, preds, reports, config)

    assert manifest.model_id == "m1"
    assert manifest.run_id == "r1"
    assert manifest.row_count == 1
    assert manifest.model_hash == "mh"
    assert manifest.calibration_status == "verified"

    report = manifest_to_report(manifest)
    assert "model_id" in report
