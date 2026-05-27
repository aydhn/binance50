import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.reliability import (
    build_reliability_bins,
    reliability_bins_to_dataframe
)

def build_pred(prob, label="1"):
    return MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label=label, predicted_class_index=1, feature_schema_hash="h",
        max_probability=prob
    )

def test_build_reliability_bins_with_labels():
    config = AppConfig()
    preds = [build_pred(0.2, "0"), build_pred(0.8, "1"), build_pred(0.9, "1")]
    labels = pd.Series([0, 1, 1])

    bins = build_reliability_bins(preds, labels, 10, config)
    assert len(bins) == 10

    # Bucket [0.8, 0.9) contains the 0.8
    b8 = bins[8]
    assert b8["count"] == 1
    assert b8["confidence"] == 0.8
    assert b8["accuracy"] == 1.0

def test_build_reliability_bins_no_labels():
    config = AppConfig()
    preds = [build_pred(0.2, "0"), build_pred(0.8, "1")]

    bins = build_reliability_bins(preds, None, 10, config)
    assert bins[8]["accuracy"] is None
    assert bins[8]["count"] == 1

def test_reliability_bins_to_dataframe():
    bins = [{"bin_start": 0.0, "count": 1}]
    df = reliability_bins_to_dataframe(bins)
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["count"] == 1
