import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLInferenceRunResult, MLInferenceRunRequest, MLInferenceStatus
from binance50.ml.inference.reports import (
    build_ml_inference_run_summary,
    build_model_load_report_view,
    build_prediction_preview_table,
    build_sandbox_output_report,
    build_ml_inference_health_report
)

def test_reports():
    config = AppConfig()
    req = MLInferenceRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", model_id="m1", dataset_id="d1", split_name="test", start_time_ms=0, end_time_ms=1, request_id="r1", correlation_id="c1")
    res = MLInferenceRunResult(request=req, run_id="r1", status=MLInferenceStatus.COMPLETED, success=True, sandbox_outputs={"signals": [1], "risks": [1, 2]})

    sum_rep = build_ml_inference_run_summary(res)
    assert sum_rep["run_id"] == "r1"

    assert build_model_load_report_view(res) == {}
    assert build_prediction_preview_table(res) == []

    sb = build_sandbox_output_report(res)
    assert sb["signal_candidates_count"] == 1
    assert sb["risk_context_count"] == 2

    health = build_ml_inference_health_report(config)
    assert health["status"] == "healthy"
    assert health["prediction_serving_forbidden"] is True
