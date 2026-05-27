import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.probability import (
    validate_probability_outputs,
    compute_probability_report,
    check_probability_sum,
    compute_max_probability,
    mark_uncalibrated_if_needed
)
from binance50.ml.inference.models import MLPredictionRow
from binance50.core.exceptions import MLProbabilityError

class MockModelResult:
    def __init__(self, cal=True):
        self.run_id = "test"
        self.calibrated = cal
        self.calibration_method = "sigmoid"

def build_pred(probs=None):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label="1", predicted_class_index=1, feature_schema_hash="h",
        probabilities=probs
    )

def test_check_probability_sum():
    assert check_probability_sum(build_pred({"0": 0.5, "1": 0.5}), 0.001) is True
    assert check_probability_sum(build_pred({"0": 0.6, "1": 0.5}), 0.001) is False

def test_compute_max_probability():
    assert compute_max_probability(build_pred({"0": 0.2, "1": 0.8})) == 0.8

def test_validate_probability_outputs():
    config = AppConfig()
    validate_probability_outputs([build_pred({"0": 0.5, "1": 0.5})], config)

    with pytest.raises(MLProbabilityError, match="Probability out of range"):
        validate_probability_outputs([build_pred({"0": -0.1, "1": 1.1})], config)

    with pytest.raises(MLProbabilityError, match="Probability sum invalid"):
        validate_probability_outputs([build_pred({"0": 0.5, "1": 0.6})], config)

def test_mark_uncalibrated():
    preds = [build_pred({"0": 0.5, "1": 0.5})]
    res = mark_uncalibrated_if_needed(preds, MockModelResult(cal=False))
    assert res[0].calibrated is False
    assert res[0].calibration_method is None

def test_compute_probability_report():
    config = AppConfig()
    preds = [build_pred({"0": 0.2, "1": 0.8}), build_pred({"0": 0.4, "1": 0.6})]
    rep = compute_probability_report(preds, MockModelResult(), config)

    assert rep.probability_available is True
    assert rep.probability_min == 0.2
    assert rep.probability_max == 0.8
    assert rep.probability_sum_invalid_count == 0
    assert rep.uncalibrated_warning is False

    rep2 = compute_probability_report(preds, MockModelResult(cal=False), config)
    assert rep2.uncalibrated_warning is True
