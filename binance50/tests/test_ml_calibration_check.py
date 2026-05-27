import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.calibration_check import (
    build_inference_calibration_check,
    extract_labels_for_predictions,
    validate_calibration_check_report
)
from binance50.core.exceptions import MLCalibrationCheckError

class MockDataset:
    def __init__(self, df):
        self.dataset_df = df

class MockModel:
    def __init__(self):
        self.run_id = "test"
        self.training_brier_score = 0.1
        self.training_ece = 0.02

def build_pred(prob):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label="1", predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob
    )

def test_extract_labels():
    ds = MockDataset(pd.DataFrame({"label": [1, 0, 1]}))
    preds = [build_pred(0.9), build_pred(0.1)]
    labels = extract_labels_for_predictions(ds, preds, "label")
    assert len(labels) == 2
    assert list(labels.values) == [1, 0]

def test_build_inference_calibration_check_no_labels():
    config = AppConfig()
    preds = [build_pred(0.9)]
    rep = build_inference_calibration_check(preds, None, MockModel(), config)
    assert rep.labels_available is False
    assert "Labels missing" in rep.warnings[0]

def test_build_inference_calibration_check_with_labels():
    config = AppConfig()
    preds = [build_pred(0.9), build_pred(0.1)]
    labels = pd.Series([1, 0])

    rep = build_inference_calibration_check(preds, labels, MockModel(), config)
    assert rep.labels_available is True
    assert rep.brier_score is not None
    assert rep.expected_calibration_error is not None
    assert rep.brier_degradation is not None

def test_validate_calibration_check_report():
    config = AppConfig()
    config.ml_inference.calibration_check.require_label_for_calibration_metrics = True

    rep = build_inference_calibration_check([], None, MockModel(), config)
    with pytest.raises(MLCalibrationCheckError, match="Labels required"):
        validate_calibration_check_report(rep, config)
