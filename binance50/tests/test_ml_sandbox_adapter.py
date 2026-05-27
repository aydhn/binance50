import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.sandbox_adapter import MLSandboxAdapter
from binance50.core.exceptions import MLSandboxIntegrationError

def build_pred(prob, label="1"):
    return MLPredictionRow(
        prediction_id="p1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob, confidence=prob
    )

def test_build_sandbox_signal_candidates():
    config = AppConfig()
    adapter = MLSandboxAdapter()
    preds = [build_pred(0.8)]

    sigs = adapter.build_sandbox_signal_candidates(preds, {}, config)
    assert len(sigs) == 1
    assert sigs[0].source_prediction_id == "p1"
    assert sigs[0].blocked_from_signal_engine is True
    assert sigs[0].explanation != ""

def test_build_sandbox_risk_context():
    config = AppConfig()
    adapter = MLSandboxAdapter()
    preds = [build_pred(0.8)]

    class MockCalRep:
        calibration_status = "verified"

    risks = adapter.build_sandbox_risk_context(preds, {"calibration": MockCalRep()}, config)
    assert len(risks) == 1
    assert risks[0].calibration_status == "verified"
    assert risks[0].blocked_from_risk_engine is True
    assert risks[0].explanation != ""

def test_block_production_writes():
    config = AppConfig()
    adapter = MLSandboxAdapter()

    preds = [build_pred(0.8)]
    sigs = adapter.build_sandbox_signal_candidates(preds, {}, config)
    risks = adapter.build_sandbox_risk_context(preds, {}, config)

    # Should not raise
    adapter.block_production_writes({"signals": sigs, "risks": risks}, config)

    sigs[0].blocked_from_signal_engine = False
    with pytest.raises(MLSandboxIntegrationError, match="blocked from production signal engine"):
        adapter.block_production_writes({"signals": sigs}, config)
