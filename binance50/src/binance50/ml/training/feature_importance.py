import pandas as pd
from typing import Any, Dict, List
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLFeatureImportanceReport

def extract_tree_feature_importance(estimator: Any, feature_columns: List[str]) -> Dict[str, float]:
    if hasattr(estimator, "feature_importances_"):
        return dict(zip(feature_columns, estimator.feature_importances_))
    return {}

def extract_linear_coefficients(estimator: Any, feature_columns: List[str]) -> Dict[str, float]:
    if hasattr(estimator, "coef_"):
        coefs = estimator.coef_[0] if estimator.coef_.ndim > 1 else estimator.coef_
        return dict(zip(feature_columns, coefs))
    return {}

def build_feature_importance_table(importances: Dict[str, float], max_features: int) -> List[Dict[str, Any]]:
    sorted_features = sorted(importances.items(), key=lambda x: abs(x[1]), reverse=True)
    return [{"feature": k, "importance": v} for k, v in sorted_features[:max_features]]

def compute_native_feature_importance(estimator: Any, feature_columns: List[str], config: AppConfig) -> MLFeatureImportanceReport:
    warnings = []
    raw = {}
    method = "native"

    if hasattr(estimator, "feature_importances_"):
        raw = extract_tree_feature_importance(estimator, feature_columns)
        if config.ml_training.feature_importance.warn_high_cardinality_importance_bias:
            warnings.append("Tree impurity importance may be biased towards high-cardinality features.")
    elif hasattr(estimator, "coef_"):
        raw = extract_linear_coefficients(estimator, feature_columns)
        method = "linear_coefficients"
    else:
        warnings.append(f"Estimator {type(estimator).__name__} does not support native feature importance.")

    top_features = build_feature_importance_table(raw, config.ml_training.feature_importance.max_features_reported)

    report = MLFeatureImportanceReport(
        model_id="unknown",
        method=method,
        split="train",
        top_features=top_features,
        raw_importances=raw,
        warnings=warnings
    )
    validate_feature_importance_report(report, config)
    return report

def validate_feature_importance_report(report: MLFeatureImportanceReport, config: AppConfig) -> None:
    if len(report.top_features) > config.ml_training.feature_importance.max_features_reported:
        raise ValueError("Exceeded max_features_reported")
