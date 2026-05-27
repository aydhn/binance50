import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.feature_matrix import (
    build_inference_feature_matrix,
    validate_inference_features,
    enforce_training_feature_order
)
from binance50.core.exceptions import MLFeatureSchemaError

class MockModelResult:
    def __init__(self, cols):
        self.feature_schema = {"columns": cols}

class MockDatasetResult:
    def __init__(self, df):
        self.dataset_df = df

def test_enforce_training_feature_order():
    df = pd.DataFrame({"f2": [1], "f1": [2]})
    ordered = enforce_training_feature_order(df, ["f1", "f2"])
    assert list(ordered.columns) == ["f1", "f2"]

def test_validate_inference_features_nan_inf():
    config = AppConfig()
    import numpy as np
    df = pd.DataFrame({"f1": [1, np.nan]})
    with pytest.raises(MLFeatureSchemaError, match="NaN/Inf"):
        validate_inference_features(df, config)

def test_validate_inference_features_forbidden_cols():
    config = AppConfig()
    df = pd.DataFrame({"f1": [1], "label_5": [0]})
    with pytest.raises(MLFeatureSchemaError, match="Forbidden column detected"):
        validate_inference_features(df, config)

def test_build_inference_feature_matrix():
    config = AppConfig()
    df = pd.DataFrame({"f1": [1, 2], "f2": [3, 4]})
    model_res = MockModelResult(["f1", "f2"])
    ds_res = MockDatasetResult(df)

    mat = build_inference_feature_matrix(ds_res, model_res, "test", config)
    assert mat.feature_columns == ["f1", "f2"]
    assert len(mat.row_metadata) == 2
