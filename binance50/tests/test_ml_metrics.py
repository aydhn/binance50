import pytest
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.training.metrics import (
    compute_classification_metrics, compute_regression_metrics,
    safe_roc_auc, safe_pr_auc, safe_log_loss, safe_brier_score,
    validate_metric_values
)
from binance50.ml.training.models import MLClassificationMetrics

class MockEstimator:
    def predict(self, X):
        return np.array([0, 1, 0, 1])
    def predict_proba(self, X):
        return np.array([[0.9, 0.1], [0.1, 0.9], [0.8, 0.2], [0.2, 0.8]])

class MockRegressor:
    def predict(self, X):
        return np.array([1.0, 2.0, 3.0, 4.0])

def test_compute_classification_metrics():
    config = AppConfig()
    est = MockEstimator()
    X = pd.DataFrame({"A": [1, 2, 3, 4]})
    y = pd.Series([0, 1, 0, 1])

    metrics = compute_classification_metrics(est, X, y, "train", config)
    assert metrics.accuracy == 1.0
    assert metrics.roc_auc == 1.0

def test_compute_regression_metrics():
    config = AppConfig()
    est = MockRegressor()
    X = pd.DataFrame({"A": [1, 2, 3, 4]})
    y = pd.Series([1.0, 2.0, 3.0, 4.0])

    metrics = compute_regression_metrics(est, X, y, "train", config)
    assert metrics.mae == 0.0
    assert metrics.rmse == 0.0

def test_safe_metrics_single_class():
    y_true = np.array([0, 0, 0])
    y_score = np.array([0.1, 0.2, 0.3])
    assert safe_roc_auc(y_true, y_score) is None
    assert safe_pr_auc(y_true, y_score) is None

def test_validate_metric_values():
    config = AppConfig()
    m = MLClassificationMetrics(accuracy=np.nan, balanced_accuracy=0.5, precision=0.5, recall=0.5, f1=0.5, confusion_matrix=[], class_distribution={})
    with pytest.raises(ValueError, match="contains NaN or inf"):
        validate_metric_values(m, config)
