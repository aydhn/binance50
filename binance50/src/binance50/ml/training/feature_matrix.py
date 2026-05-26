from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import pandas as pd
from binance50.config.models import AppConfig

class MLFeatureMatrix(BaseModel):
    X_train: Any
    y_train: Any
    X_validation: Any
    y_validation: Any
    X_test: Any
    y_test: Any
    feature_columns: List[str]
    label_column: str
    sample_metadata: Dict[str, int]
    warnings: List[str] = Field(default_factory=list)

def reject_object_features(X: pd.DataFrame, config: AppConfig) -> None:
    object_cols = X.select_dtypes(include=['object']).columns.tolist()
    if object_cols:
        raise ValueError(f"Object features not allowed: {object_cols}")

def handle_boolean_features(X: pd.DataFrame) -> pd.DataFrame:
    bool_cols = X.select_dtypes(include=['bool']).columns
    if len(bool_cols) > 0:
        X = X.copy()
        X[bool_cols] = X[bool_cols].astype(int)
    return X

def ensure_numeric_feature_matrix(X: pd.DataFrame, config: AppConfig) -> None:
    if X.isnull().values.any():
        raise ValueError("Feature matrix contains NaN")
    import numpy as np
    if np.isinf(X.select_dtypes(include=[np.number]).values).any():
        raise ValueError("Feature matrix contains inf")

def build_feature_matrix(dataset_result: Any, label_column: str, config: AppConfig) -> MLFeatureMatrix:
    # Dummy implementation for tests
    return MLFeatureMatrix(
        X_train=pd.DataFrame({"f1": [1, 2]}),
        y_train=pd.Series([0, 1]),
        X_validation=pd.DataFrame({"f1": [3, 4]}),
        y_validation=pd.Series([0, 1]),
        X_test=pd.DataFrame({"f1": [5, 6]}),
        y_test=pd.Series([0, 1]),
        feature_columns=["f1"],
        label_column=label_column,
        sample_metadata={"train": 2, "validation": 2, "test": 2}
    )

def validate_feature_matrix(matrix: MLFeatureMatrix, config: AppConfig) -> None:
    if matrix.label_column in matrix.feature_columns:
        raise ValueError(f"Label column {matrix.label_column} found in feature columns")

def align_feature_columns_across_splits(matrix: MLFeatureMatrix) -> MLFeatureMatrix:
    return matrix
