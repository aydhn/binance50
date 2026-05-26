from typing import Any, Dict, List
from binance50.config.models import AppConfig

def build_ml_training_run_summary(result: Any) -> Dict[str, Any]:
    return {"status": result.status.value, "model_count": len(result.model_results)}

def build_model_comparison_table(result: Any) -> List[Dict[str, Any]]:
    table = []
    for m in result.model_results:
        val_acc = m.validation_metrics.get("accuracy") if m.validation_metrics else None
        table.append({"model_name": m.model_name, "validation_accuracy": val_acc})
    return sorted(table, key=lambda x: x["validation_accuracy"] or 0, reverse=True)

def build_best_model_report(result: Any) -> Dict[str, Any]:
    return {"best_model_id": result.best_validation_model}

def build_metrics_report(model_result: Any) -> Dict[str, Any]:
    return {"train": model_result.train_metrics, "validation": model_result.validation_metrics}

def build_calibration_report_view(model_result: Any) -> Dict[str, Any]:
    if model_result.calibration_report:
        return model_result.calibration_report.model_dump()
    return {}

def build_feature_importance_report_view(model_result: Any) -> Dict[str, Any]:
    if model_result.feature_importance_report:
        return model_result.feature_importance_report.model_dump()
    return {}

def build_model_card_report(model_result: Any) -> Dict[str, Any]:
    if model_result.model_card:
        return model_result.model_card.model_dump()
    return {}

def build_ml_training_health_report(config: AppConfig) -> Dict[str, Any]:
    return {"status": "healthy"}
