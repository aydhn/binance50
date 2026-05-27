import hashlib
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.core.exceptions import MLFeatureSchemaError

class MLFeatureSchemaCheckReport(BaseModel):
    model_id: str
    dataset_id: str
    expected_feature_count: int
    actual_feature_count: int
    exact_columns_match: bool
    exact_order_match: bool
    missing_features: List[str] = Field(default_factory=list)
    extra_features: List[str] = Field(default_factory=list)
    dtype_mismatches: Dict[str, str] = Field(default_factory=dict)
    schema_hash_expected: str
    schema_hash_actual: str
    passed: bool
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

def build_expected_feature_schema(model_result: Any) -> Dict[str, Any]:
    return getattr(model_result, "feature_schema", {"columns": [], "dtypes": {}})

def build_actual_feature_schema(dataset_result: Any) -> Dict[str, Any]:
    return getattr(dataset_result, "feature_schema", {"columns": [], "dtypes": {}})

def compute_feature_schema_hash(feature_columns: List[str], dtypes: Dict[str, str] = None) -> str:
    schema = {"columns": feature_columns}
    if dtypes:
        schema["dtypes"] = dtypes

    schema_str = json.dumps(schema, sort_keys=True)
    return hashlib.sha256(schema_str.encode()).hexdigest()

def compare_feature_schema(expected: Dict[str, Any], actual: Dict[str, Any], config: AppConfig) -> MLFeatureSchemaCheckReport:
    exp_cols = expected.get("columns", [])
    act_cols = actual.get("columns", [])

    missing = [c for c in exp_cols if c not in act_cols]
    extra = [c for c in act_cols if c not in exp_cols]

    exact_match = (set(exp_cols) == set(act_cols))
    order_match = (exp_cols == act_cols) if exact_match else False

    exp_hash = compute_feature_schema_hash(exp_cols)
    act_hash = compute_feature_schema_hash(act_cols)

    passed = True
    warnings = []

    if missing and not config.ml_inference.feature_schema.allow_missing_features:
        passed = False

    if extra and not config.ml_inference.feature_schema.allow_extra_features:
        passed = False

    if config.ml_inference.feature_schema.require_exact_feature_columns and not exact_match:
        passed = False

    if config.ml_inference.feature_schema.require_exact_feature_order and not order_match:
        passed = False

    return MLFeatureSchemaCheckReport(
        model_id="unknown",
        dataset_id="unknown",
        expected_feature_count=len(exp_cols),
        actual_feature_count=len(act_cols),
        exact_columns_match=exact_match,
        exact_order_match=order_match,
        missing_features=missing,
        extra_features=extra,
        schema_hash_expected=exp_hash,
        schema_hash_actual=act_hash,
        passed=passed,
        warnings=warnings
    )

def validate_feature_schema_for_inference(report: MLFeatureSchemaCheckReport, config: AppConfig) -> None:
    if not report.passed:
        err_msg = []
        if report.missing_features:
            err_msg.append(f"Missing features: {report.missing_features}")
        if report.extra_features:
            err_msg.append(f"Extra features: {report.extra_features}")
        if not report.exact_order_match and config.ml_inference.feature_schema.require_exact_feature_order:
            err_msg.append("Feature order mismatch")

        raise MLFeatureSchemaError(f"Feature schema check failed: {', '.join(err_msg)}")
