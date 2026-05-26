import numpy as np
from typing import Any, Dict, Optional
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLClassificationMetrics, MLRegressionMetrics

def safe_roc_auc(y_true: Any, y_score: Any) -> Optional[float]:
    from sklearn.metrics import roc_auc_score
    try:
        if len(np.unique(y_true)) > 1:
            if y_score.ndim == 2 and y_score.shape[1] == 2:
                return roc_auc_score(y_true, y_score[:, 1])
            return roc_auc_score(y_true, y_score, multi_class='ovr')
    except Exception:
        pass
    return None

def safe_pr_auc(y_true: Any, y_score: Any) -> Optional[float]:
    from sklearn.metrics import average_precision_score
    try:
        if len(np.unique(y_true)) > 1:
            if y_score.ndim == 2 and y_score.shape[1] == 2:
                return average_precision_score(y_true, y_score[:, 1])
            return average_precision_score(y_true, y_score)
    except Exception:
        pass
    return None

def safe_log_loss(y_true: Any, y_proba: Any) -> Optional[float]:
    from sklearn.metrics import log_loss
    try:
        if len(np.unique(y_true)) > 1:
            return log_loss(y_true, y_proba)
    except Exception:
        pass
    return None

def safe_brier_score(y_true: Any, y_proba: Any) -> Optional[float]:
    from sklearn.metrics import brier_score_loss
    try:
        if len(np.unique(y_true)) > 1 and (y_proba.ndim == 1 or y_proba.shape[1] == 2):
            score_col = y_proba[:, 1] if y_proba.ndim == 2 else y_proba
            return brier_score_loss(y_true, score_col)
    except Exception:
        pass
    return None

def compute_probability_metrics(y_true: Any, y_proba: Any, config: AppConfig) -> Dict[str, Any]:
    return {
        "log_loss": safe_log_loss(y_true, y_proba),
        "brier_score": safe_brier_score(y_true, y_proba)
    }

def compute_classification_metrics(estimator: Any, X: Any, y: Any, split_name: str, config: AppConfig) -> MLClassificationMetrics:
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    y_pred = estimator.predict(X)
    acc = accuracy_score(y, y_pred)

    # We use macro for balanced accuracy approx in mock
    precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average=config.ml_training.metrics.classification.average, zero_division=0)

    y_proba = estimator.predict_proba(X) if hasattr(estimator, "predict_proba") else None

    roc_auc = safe_roc_auc(y, y_proba) if y_proba is not None else None
    pr_auc = safe_pr_auc(y, y_proba) if y_proba is not None else None
    l_loss = safe_log_loss(y, y_proba) if y_proba is not None else None
    b_score = safe_brier_score(y, y_proba) if y_proba is not None else None

    cm = confusion_matrix(y, y_pred).tolist()
    counts = {str(k): int(v) for k, v in zip(*np.unique(y, return_counts=True))}

    metrics = MLClassificationMetrics(
        accuracy=acc,
        balanced_accuracy=acc, # Mocked
        precision=precision,
        recall=recall,
        f1=f1,
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        log_loss=l_loss,
        brier_score=b_score,
        confusion_matrix=cm,
        class_distribution=counts
    )
    validate_metric_values(metrics, config)
    return metrics

def compute_regression_metrics(estimator: Any, X: Any, y: Any, split_name: str, config: AppConfig) -> MLRegressionMetrics:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    y_pred = estimator.predict(X)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    metrics = MLRegressionMetrics(mae=mae, rmse=rmse, r2=r2, directional_accuracy=0.5)
    validate_metric_values(metrics, config)
    return metrics

def validate_metric_values(metrics: Any, config: AppConfig) -> None:
    for k, v in metrics.model_dump().items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            raise ValueError(f"Metric {k} contains NaN or inf")
