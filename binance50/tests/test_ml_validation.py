import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.validation import MLTimeSeriesValidationEngine
from binance50.ml.training.feature_matrix import MLFeatureMatrix

def test_validation_engine():
    config = AppConfig()
    engine = MLTimeSeriesValidationEngine()

    res = engine.run_holdout_validation(None, None, config)
    assert res["status"] == "success"

    cv_res = engine.run_time_series_cv(None, None, "model", config)
    assert cv_res["status"] == "success"

    rep = engine.build_validation_report(None)
    assert rep["validation_method"] == "time_series_split"
