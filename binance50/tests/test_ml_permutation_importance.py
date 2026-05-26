import pytest
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.training.permutation_importance import (
    compute_permutation_importance_report, validate_permutation_split
)

class MockEstimator:
    def fit(self, X, y):
        return self
    def predict(self, X):
        return np.ones(len(X))
    def score(self, X, y):
        return 1.0

def test_validate_permutation_split():
    config = AppConfig()
    config.ml_training.validation.test_set_final_report_only = True
    # Should not raise
    validate_permutation_split("test", config)

def test_compute_permutation_importance_report():
    config = AppConfig()
    X = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    y = pd.Series([1, 1])
    est = MockEstimator()

    rep = compute_permutation_importance_report(est, X, y, ["A", "B"], "validation", config)
    assert rep.method == "permutation"
    assert len(rep.top_features) <= config.ml_training.feature_importance.max_features_reported
