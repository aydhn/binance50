from typing import Any, Dict, List
import datetime
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLInferenceManifest, MLPredictionRow

def build_inference_manifest(result_context: Dict[str, Any], predictions: List[MLPredictionRow], reports: Dict[str, Any], config: AppConfig) -> MLInferenceManifest:
    model_id = result_context.get("model_id", "unknown")
    run_id = result_context.get("run_id", "unknown")
    artifact_id = result_context.get("artifact_id", "unknown")
    dataset_id = result_context.get("dataset_id", "unknown")
    split_name = result_context.get("split_name", "unknown")

    # Normally computed during reproducibility step
    feature_schema_hash = result_context.get("feature_schema_hash", "unknown")
    model_hash = result_context.get("model_hash", "unknown")
    dataset_hash = result_context.get("dataset_hash", "unknown")
    preprocessor_hash = result_context.get("preprocessor_hash", "unknown")
    config_hash = result_context.get("config_hash", "unknown")
    output_hash = result_context.get("output_hash", "unknown")

    cal_rep = reports.get("calibration")
    calibration_status = getattr(cal_rep, "calibration_status", "unknown") if cal_rep else "unknown"

    return MLInferenceManifest(
        inference_id=f"inf_{run_id}",
        run_id=run_id,
        model_id=model_id,
        artifact_id=artifact_id,
        dataset_id=dataset_id,
        split_name=split_name,
        row_count=len(predictions),
        prediction_count=len(predictions),
        feature_schema_hash=feature_schema_hash,
        model_hash=model_hash,
        dataset_hash=dataset_hash,
        preprocessor_hash=preprocessor_hash,
        config_hash=config_hash,
        output_hash=output_hash,
        calibration_status=calibration_status,
        created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

def validate_inference_manifest(manifest: MLInferenceManifest, config: AppConfig) -> None:
    pass

def manifest_to_report(manifest: MLInferenceManifest) -> Dict[str, Any]:
    # Dummy mock
    return manifest.model_dump()
