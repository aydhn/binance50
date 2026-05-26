from typing import Any, Dict
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLModelOverfitReport

def compute_metric_gap(train_metrics: Dict[str, Any], validation_metrics: Dict[str, Any], metric_name: str) -> float:
    train_val = train_metrics.get(metric_name)
    val_val = validation_metrics.get(metric_name)
    if train_val is not None and val_val is not None:
        return float(train_val - val_val)
    return 0.0

def classify_ml_overfit_risk(report: MLModelOverfitReport, config: AppConfig) -> str:
    if report.train_validation_metric_gap is not None and report.train_validation_metric_gap > config.ml_training.overfit.max_train_validation_metric_gap:
        return "high"
    return "low"

def build_ml_overfit_report(model_result: Any, dummy_result: Any, config: AppConfig) -> MLModelOverfitReport:
    warnings = []

    if not model_result.train_metrics or not model_result.validation_metrics:
        return MLModelOverfitReport(
            model_id=model_result.model_id,
            overfit_risk_level="unknown",
            worse_than_dummy_warning=False,
            train_much_better_warning=False,
            test_degradation_warning=False,
            warnings=["Missing metrics for overfit report"]
        )

    acc_gap = compute_metric_gap(model_result.train_metrics, model_result.validation_metrics, "accuracy")
    auc_gap = compute_metric_gap(model_result.train_metrics, model_result.validation_metrics, "roc_auc")

    worse_than_dummy = False
    validation_vs_dummy_gap = 0.0
    if dummy_result and dummy_result.validation_metrics:
        val_acc = model_result.validation_metrics.get("accuracy", 0)
        dummy_acc = dummy_result.validation_metrics.get("accuracy", 0)
        validation_vs_dummy_gap = val_acc - dummy_acc
        if validation_vs_dummy_gap < 0:
            worse_than_dummy = True
            if config.ml_training.overfit.warn_if_validation_worse_than_dummy:
                warnings.append("Validation metric is worse than dummy baseline")

    train_much_better = False
    if acc_gap > config.ml_training.overfit.max_train_validation_metric_gap:
        train_much_better = True
        if config.ml_training.overfit.warn_if_train_much_better:
            warnings.append("Train metric is significantly better than validation")

    test_deg = False
    val_test_gap = 0.0
    if model_result.test_metrics:
        val_test_gap = compute_metric_gap(model_result.validation_metrics, model_result.test_metrics, "accuracy")
        if val_test_gap > config.ml_training.overfit.test_degradation_warning_gap:
            test_deg = True
            warnings.append("Test set shows significant degradation compared to validation")

    report = MLModelOverfitReport(
        model_id=model_result.model_id,
        train_validation_metric_gap=acc_gap,
        train_validation_auc_gap=auc_gap,
        validation_test_gap=val_test_gap,
        validation_vs_dummy_gap=validation_vs_dummy_gap,
        overfit_risk_level="unknown",
        worse_than_dummy_warning=worse_than_dummy,
        train_much_better_warning=train_much_better,
        test_degradation_warning=test_deg,
        warnings=warnings
    )
    report.overfit_risk_level = classify_ml_overfit_risk(report, config)
    validate_overfit_report(report, config)
    return report

def validate_overfit_report(report: MLModelOverfitReport, config: AppConfig) -> None:
    if config.ml_training.overfit.reject_if_validation_worse_than_dummy and report.worse_than_dummy_warning:
        raise ValueError("Model validation is worse than dummy baseline")
