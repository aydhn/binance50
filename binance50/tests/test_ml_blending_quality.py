import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.quality import build_ml_blending_quality_report, assert_ml_blending_quality_passed
from binance50.ml.blending.models import MLBlendingRunResult, MLBlendingRunRequest, MLBlendingStatus
from binance50.core.exceptions import MLBlendingQualityError

def test_build_quality_report():
    config = AppConfig()
    req = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    res = MLBlendingRunResult(request=req, run_id="1", status=MLBlendingStatus.completed)
    report = build_ml_blending_quality_report(res, config)
    assert report.status == "passed"

def test_assert_quality_passed():
    config = AppConfig()
    req = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    res = MLBlendingRunResult(request=req, run_id="1", status=MLBlendingStatus.completed)
    report = build_ml_blending_quality_report(res, config)
    assert_ml_blending_quality_passed(report, config)
    report.status = "failed"
    with pytest.raises(MLBlendingQualityError):
        assert_ml_blending_quality_passed(report, config)
