import pytest
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.training.calibration import (
    calibrate_classifier_if_enabled, build_uncalibrated_report,
    compute_reliability_bins, compute_expected_calibration_error
)

class MockMatrix:
    X_validation = pd.DataFrame({"A": [1, 2, 3, 4]})
    y_validation = pd.Series([0, 1, 0, 1])

from sklearn.linear_model import LogisticRegression
class MockEstimator(LogisticRegression):
    def predict_proba(self, X):
        return np.array([[0.9, 0.1], [0.1, 0.9], [0.8, 0.2], [0.2, 0.8]])[:len(X)]

def test_calibrate_classifier_if_enabled():
    config = AppConfig()
    config.ml_training.calibration.enabled = True
    config.ml_training.calibration.calibrate_classifiers = True
    config.ml_training.calibration.method = "sigmoid"
    config.ml_training.calibration.calibration_split = "validation"

    est = MockEstimator()
    matrix = MockMatrix()

    cal, rep = calibrate_classifier_if_enabled(est, matrix, config)
    assert rep.calibrated is True
    assert rep.method == "sigmoid"

def test_uncalibrated_report():
    config = AppConfig()
    config.ml_training.calibration.warn_uncalibrated_probabilities = True
    rep = build_uncalibrated_report(None, None, config)
    assert rep.calibrated is False
    assert "uncalibrated" in rep.warnings

def test_compute_calibration_curves():
    y_true = np.array([0, 1, 0, 1])
    y_proba = np.array([0.1, 0.9, 0.2, 0.8])
    bins = compute_reliability_bins(y_true, y_proba, 2)
    assert len(bins) > 0
    ece = compute_expected_calibration_error(y_true, y_proba, 2)
    assert ece is not None
