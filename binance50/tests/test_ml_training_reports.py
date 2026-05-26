import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.reports import (
    build_ml_training_run_summary, build_model_comparison_table,
    build_best_model_report, build_metrics_report,
    build_calibration_report_view, build_feature_importance_report_view,
    build_model_card_report, build_ml_training_health_report
)

class MockResult:
    status = type('obj', (object,), {'value': 'completed'})
    model_results = []
    best_validation_model = "m1"

def test_reports_basics():
    res = MockResult()
    assert build_ml_training_run_summary(res)["status"] == "completed"
    assert build_model_comparison_table(res) == []
    assert build_best_model_report(res)["best_model_id"] == "m1"
    assert build_ml_training_health_report(AppConfig())["status"] == "healthy"
