import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow
from binance50.ml.inference.drift import build_inference_drift_report

class MockModelResult:
    def __init__(self):
        self.run_id = "test"
        self.feature_stats = {"a": 1}
        self.prediction_stats = {"b": 2}

def test_build_inference_drift_report():
    config = AppConfig()
    df = pd.DataFrame({"f1": [1, 2]})
    preds = [MLPredictionRow(
        prediction_id="1", model_id="m", dataset_id="d", symbol="BTC", market_scope="spot", interval="1m",
        open_time="now", predicted_label="1", predicted_class_index=1, feature_schema_hash="h"
    )]

    rep = build_inference_drift_report(df, preds, MockModelResult(), config)

    assert rep.skeleton_only is True
    assert rep.compare_to_training_feature_stats is True
    assert "shift_detected" in rep.feature_shift_summary
    assert "shift_detected" in rep.prediction_shift_summary
    assert "psi_score" in rep.psi_skeleton
    assert rep.high_feature_shift_warning is False
