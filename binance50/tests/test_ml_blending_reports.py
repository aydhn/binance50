import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.models import MLBlendingRunResult, MLBlendingRunRequest, MLBlendingStatus
from binance50.ml.blending.reports import build_ml_blending_run_summary, build_ml_blending_health_report

def test_run_summary():
    req = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    res = MLBlendingRunResult(request=req, run_id="1", status=MLBlendingStatus.completed)
    summary = build_ml_blending_run_summary(res)
    assert summary["status"] == MLBlendingStatus.completed

def test_health_report():
    config = AppConfig()
    health = build_ml_blending_health_report(config)
    assert health["status"] == "ok"
