import pytest
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.training.feature_importance import (
    compute_native_feature_importance, extract_tree_feature_importance,
    extract_linear_coefficients, build_feature_importance_table,
    validate_feature_importance_report
)

class MockTreeEstimator:
    feature_importances_ = np.array([0.2, 0.8])

class MockLinearEstimator:
    coef_ = np.array([[0.5, -1.5]])

class MockUnsupportedEstimator:
    pass

def test_extract_tree_feature_importance():
    res = extract_tree_feature_importance(MockTreeEstimator(), ["A", "B"])
    assert res["B"] == 0.8

def test_extract_linear_coefficients():
    res = extract_linear_coefficients(MockLinearEstimator(), ["A", "B"])
    assert res["B"] == -1.5

def test_build_feature_importance_table():
    raw = {"A": 0.5, "B": -1.5, "C": 0.1}
    table = build_feature_importance_table(raw, 2)
    assert len(table) == 2
    assert table[0]["feature"] == "B"

def test_compute_native_feature_importance():
    config = AppConfig()
    config.ml_training.feature_importance.warn_high_cardinality_importance_bias = True

    rep = compute_native_feature_importance(MockTreeEstimator(), ["A", "B"], config)
    assert rep.method == "native"
    assert "bias" in rep.warnings[0]

    rep2 = compute_native_feature_importance(MockLinearEstimator(), ["A", "B"], config)
    assert rep2.method == "linear_coefficients"

    rep3 = compute_native_feature_importance(MockUnsupportedEstimator(), ["A", "B"], config)
    assert "support" in rep3.warnings[0]
