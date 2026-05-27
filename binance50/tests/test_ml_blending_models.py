from binance50.ml.blending.models import MLBlendComponent, MLBlendBreakdown, MLBlendedSandboxCandidate, MLBlendingRunRequest, MLBlendingRunResult, MLBlendOutputStatus, MLBlendingIntent, MLBlendingStatus
import hashlib
import json

def test_ml_blend_component_valid():
    comp = MLBlendComponent(
        component_name="test",
        raw_value=1.0,
        normalized_value=1.0,
        weight=0.5,
        contribution=0.5,
        reason="test"
    )
    assert comp.component_name == "test"

def test_ml_blend_breakdown_valid():
    breakdown = MLBlendBreakdown(
        final_blended_score=50.0,
        final_blended_probability=0.5
    )
    assert breakdown.final_blended_score == 50.0

def test_ml_blended_sandbox_candidate_valid():
    breakdown = MLBlendBreakdown(final_blended_score=50.0, final_blended_probability=0.5)
    cand = MLBlendedSandboxCandidate(
        blended_candidate_id="test",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=0,
        close_time=0,
        direction=1,
        blended_score=50.0,
        blended_probability=0.5,
        confidence=0.0,
        status=MLBlendOutputStatus.sandbox_only,
        intent=MLBlendingIntent.sandbox_only,
        breakdown=breakdown,
        explanation="test"
    )
    assert cand.blocked_from_signal_engine is True
    assert cand.blocked_from_risk_engine is True
    assert cand.blocked_from_execution is True
    assert not hasattr(cand, "order_id")

def test_ml_blending_run_request_valid():
    req = MLBlendingRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        request_id="1",
        correlation_id="1"
    )
    assert req.symbol == "BTCUSDT"

def test_ml_blending_run_result_valid():
    req = MLBlendingRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        request_id="1",
        correlation_id="1"
    )
    res = MLBlendingRunResult(
        request=req,
        run_id="run_1",
        status=MLBlendingStatus.completed
    )
    assert res.run_id == "run_1"

def test_hash_deterministic():
    req1 = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    req2 = MLBlendingRunRequest(symbol="BTCUSDT", market_scope="spot", interval="1m", request_id="1", correlation_id="1")
    data1 = json.dumps(req1.model_dump(), sort_keys=True, default=str)
    data2 = json.dumps(req2.model_dump(), sort_keys=True, default=str)
    assert hashlib.sha256(data1.encode()).hexdigest() == hashlib.sha256(data2.encode()).hexdigest()
