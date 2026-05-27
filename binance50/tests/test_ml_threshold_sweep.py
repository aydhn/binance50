import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.threshold_sweep import run_threshold_sweep

def build_pred(prob, label="1"):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob
    )

def test_run_threshold_sweep_no_labels():
    config = AppConfig()
    preds = [build_pred(0.6), build_pred(0.8)]

    rep = run_threshold_sweep(preds, None, config)
    assert rep.labels_available is False
    assert rep.research_only is True
    assert rep.auto_apply_forbidden is True
    assert len(rep.rows) == len(config.ml_inference.threshold_sweep.thresholds)

    # 0.5 threshold should have 2 predictions
    row_05 = next(r for r in rep.rows if r.threshold == 0.5)
    assert row_05.prediction_count == 2
    assert row_05.precision is None

def test_run_threshold_sweep_with_labels():
    config = AppConfig()
    preds = [build_pred(0.6), build_pred(0.8)]
    labels = pd.Series([1, 1])

    rep = run_threshold_sweep(preds, labels, config)
    assert rep.labels_available is True

    row_05 = next(r for r in rep.rows if r.threshold == 0.5)
    assert row_05.precision is not None
