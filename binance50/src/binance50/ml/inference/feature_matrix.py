from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.core.exceptions import MLFeatureSchemaError
from binance50.ml.inference.feature_schema import MLFeatureSchemaCheckReport

class MLInferenceFeatureMatrix(BaseModel):
    X: Any
    row_metadata: List[Dict[str, Any]]
    feature_columns: List[str]
    feature_schema_report: Optional[MLFeatureSchemaCheckReport] = None
    split_name: str
    warnings: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

def select_split_for_inference(dataset_result: Any, split_name: str, config: AppConfig) -> pd.DataFrame:
    # Dummy mock
    if hasattr(dataset_result, "dataset_df"):
        return getattr(dataset_result, "dataset_df")
    return pd.DataFrame({"f1": [1, 2], "f2": [3, 4]})

def enforce_training_feature_order(X: pd.DataFrame, expected_feature_columns: List[str]) -> pd.DataFrame:
    return X[expected_feature_columns].copy()

def validate_inference_features(X: pd.DataFrame, config: AppConfig) -> None:
    if config.ml_inference.feature_schema.reject_nan_inf_features:
        if X.isna().any().any():
            raise MLFeatureSchemaError("Features contain NaN/Inf")

    if config.ml_inference.dataset.reject_if_feature_contains_label:
        for c in X.columns:
            if "label" in c.lower() or "target" in c.lower() or "future" in c.lower():
                raise MLFeatureSchemaError(f"Forbidden column detected in features: {c}")

def build_row_metadata(df: pd.DataFrame) -> List[Dict[str, Any]]:
    # Simple mock extracting row indices/times
    return [{"index": i} for i in range(len(df))]

def build_inference_feature_matrix(
    dataset_result: Any,
    model_result: Any,
    split_name: str,
    config: AppConfig
) -> MLInferenceFeatureMatrix:
    df = select_split_for_inference(dataset_result, split_name, config)
    expected_cols = getattr(model_result, "feature_schema", {}).get("columns", list(df.columns))

    validate_inference_features(df, config)

    X = enforce_training_feature_order(df, expected_cols)
    row_meta = build_row_metadata(df)

    return MLInferenceFeatureMatrix(
        X=X,
        row_metadata=row_meta,
        feature_columns=expected_cols,
        split_name=split_name
    )
