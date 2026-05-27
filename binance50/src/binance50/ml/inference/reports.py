from typing import Any, Dict, List
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLInferenceRunResult

def build_ml_inference_run_summary(result: MLInferenceRunResult) -> Dict[str, Any]:
    return {
        "run_id": result.run_id,
        "status": result.status,
        "success": result.success,
        "prediction_count": len(result.predictions)
    }

def build_model_load_report_view(result: MLInferenceRunResult) -> Dict[str, Any]:
    if not result.model_load_report:
        return {}
    return result.model_load_report.model_dump()

def build_prediction_preview_table(result: MLInferenceRunResult, limit: int = 100) -> List[Dict[str, Any]]:
    return [p.model_dump() for p in result.predictions[:limit]]

def build_probability_report_view(result: MLInferenceRunResult) -> Dict[str, Any]:
    return result.probability_report.model_dump() if result.probability_report else {}

def build_calibration_check_report_view(result: MLInferenceRunResult) -> Dict[str, Any]:
    return result.calibration_check_report.model_dump() if result.calibration_check_report else {}

def build_threshold_sweep_table(result: MLInferenceRunResult) -> List[Dict[str, Any]]:
    return [r.model_dump() for r in result.threshold_sweep_report.rows] if getattr(result, "threshold_sweep_report", None) else []

def build_distribution_report_view(result: MLInferenceRunResult) -> Dict[str, Any]:
    return result.distribution_report.model_dump() if result.distribution_report else {}

def build_confidence_bucket_report_view(result: MLInferenceRunResult) -> List[Dict[str, Any]]:
    # Mocking it returning dict since its stored as list in runner
    return []

def build_drift_report_view(result: MLInferenceRunResult) -> Dict[str, Any]:
    return result.drift_report.model_dump() if result.drift_report else {}

def build_sandbox_output_report(result: MLInferenceRunResult) -> Dict[str, Any]:
    sigs = result.sandbox_outputs.get("signals", []) if result.sandbox_outputs else []
    risks = result.sandbox_outputs.get("risks", []) if result.sandbox_outputs else []
    return {
        "signal_candidates_count": len(sigs),
        "risk_context_count": len(risks)
    }

def build_ml_inference_health_report(config: AppConfig) -> Dict[str, Any]:
    return {
        "status": "healthy",
        "real_exchange_forbidden": config.ml_inference.real_exchange_forbidden,
        "prediction_serving_forbidden": config.ml_inference.prediction_serving_forbidden
    }
