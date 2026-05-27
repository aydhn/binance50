import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.prediction_distribution import (
    analyze_prediction_distribution,
    compute_class_distribution,
    compute_probability_distribution_summary,
    detect_single_class_prediction_collapse,
    detect_low_confidence,
    detect_probability_collapse
)

def build_pred(prob, label="1"):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob
    )

def test_compute_class_distribution():
    preds = [build_pred(0.8, "1"), build_pred(0.6, "1"), build_pred(0.9, "0")]
    dist = compute_class_distribution(preds)
    assert dist["1"] == pytest.approx(0.666, 0.01)
    assert dist["0"] == pytest.approx(0.333, 0.01)

def test_compute_probability_distribution_summary():
    preds = [build_pred(0.2), build_pred(0.4), build_pred(0.6)]
    summary = compute_probability_distribution_summary(preds)
    assert summary["min"] == 0.2
    assert summary["max"] == 0.6
    assert summary["mean"] == pytest.approx(0.4, 0.01)

def test_detectors():
    config = AppConfig()
    preds_collapse = [build_pred(0.8, "1")] * 10
    preds_low_conf = [build_pred(0.51, "1")] * 10

    assert detect_single_class_prediction_collapse(preds_collapse, config) is True
    assert detect_low_confidence(preds_low_conf, config) is True
    assert detect_probability_collapse(preds_collapse, config) is True

def test_analyze_prediction_distribution():
    config = AppConfig()
    preds = [build_pred(0.8, "1"), build_pred(0.6, "1"), build_pred(0.9, "0")]

    rep = analyze_prediction_distribution(preds, config)
    assert rep.row_count == 3
    assert rep.single_class_ratio == pytest.approx(0.666, 0.01)
