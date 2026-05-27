import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.confidence import (
    compute_confidence_for_prediction,
    build_confidence_buckets,
    confidence_buckets_to_dataframe,
    summarize_confidence_buckets
)

def build_pred(prob, label="1"):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob
    )

def test_compute_confidence():
    assert compute_confidence_for_prediction(build_pred(0.8)) == 0.8

def test_build_confidence_buckets():
    config = AppConfig()
    preds = [build_pred(0.55, "1"), build_pred(0.65, "1"), build_pred(0.75, "0")]
    labels = pd.Series([1, 1, 1])

    buckets = build_confidence_buckets(preds, labels, config)

    # default buckets are [0.0, 0.5], [0.5, 0.6], [0.6, 0.7], [0.7, 0.8], [0.8, 0.9], [0.9, 1.0]
    assert len(buckets) == 6

    b56 = next(b for b in buckets if b.bucket_start == 0.5)
    assert b56.count == 1
    assert b56.accuracy_if_labels_available == 1.0

    b78 = next(b for b in buckets if b.bucket_start == 0.7)
    assert b78.count == 1
    assert b78.accuracy_if_labels_available == 0.0

def test_dataframe_and_summary():
    config = AppConfig()
    preds = [build_pred(0.55, "1")]
    buckets = build_confidence_buckets(preds, None, config)

    df = confidence_buckets_to_dataframe(buckets)
    assert len(df) == 6

    summary = summarize_confidence_buckets(buckets)
    assert summary["total_buckets"] == 6
