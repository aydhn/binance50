import pytest
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.training.feature_matrix import (
    MLFeatureMatrix, reject_object_features, handle_boolean_features,
    ensure_numeric_feature_matrix, validate_feature_matrix
)

def test_reject_object_features():
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    with pytest.raises(ValueError, match="Object features not allowed"):
        reject_object_features(df, AppConfig())

def test_handle_boolean_features():
    df = pd.DataFrame({"A": [True, False]})
    res = handle_boolean_features(df)
    assert res["A"].dtype == int
    assert res["A"].tolist() == [1, 0]

def test_ensure_numeric_feature_matrix():
    df = pd.DataFrame({"A": [1.0, np.nan]})
    with pytest.raises(ValueError, match="Feature matrix contains NaN"):
        ensure_numeric_feature_matrix(df, AppConfig())

    df2 = pd.DataFrame({"A": [1.0, np.inf]})
    with pytest.raises(ValueError, match="Feature matrix contains inf"):
        ensure_numeric_feature_matrix(df2, AppConfig())

def test_validate_feature_matrix():
    matrix = MLFeatureMatrix(
        X_train=None, y_train=None, X_validation=None, y_validation=None, X_test=None, y_test=None,
        feature_columns=["f1", "label"], label_column="label", sample_metadata={}
    )
    with pytest.raises(ValueError, match="Label column label found in feature columns"):
        validate_feature_matrix(matrix, AppConfig())
