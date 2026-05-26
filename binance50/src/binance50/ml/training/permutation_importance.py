import pandas as pd
from typing import Any, List
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLFeatureImportanceReport
from .feature_importance import build_feature_importance_table

def validate_permutation_split(split_name: str, config: AppConfig) -> None:
    if split_name == "test" and config.ml_training.validation.test_set_final_report_only:
        pass # Only warning if necessary, handled at caller level

def compute_permutation_importance_report(estimator: Any, X: Any, y: Any, feature_columns: List[str], split_name: str, config: AppConfig) -> MLFeatureImportanceReport:
    validate_permutation_split(split_name, config)

    from sklearn.inspection import permutation_importance
    result = permutation_importance(
        estimator,
        X,
        y,
        n_repeats=config.ml_training.feature_importance.permutation_n_repeats,
        random_state=config.ml_training.feature_importance.permutation_random_state,
        n_jobs=config.ml_training.models.n_jobs
    )

    raw = dict(zip(feature_columns, result.importances_mean))
    top_features = build_feature_importance_table(raw, config.ml_training.feature_importance.max_features_reported)

    return MLFeatureImportanceReport(
        model_id="unknown",
        method="permutation",
        split=split_name,
        top_features=top_features,
        raw_importances=raw
    )
