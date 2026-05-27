from typing import Any

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardRunResult
from binance50.walkforward.validators import validate_no_live_or_paper_intent


def import_walkforward_result(result: WalkForwardRunResult, config: AppConfig) -> Any:
    validate_no_live_or_paper_intent(getattr(result, "request", {}))

    # Dummy manifest implementation
    class DatasetManifest:
        pass

    return DatasetManifest()

from binance50.ml.datasets.models import MLDatasetBuildResult
from binance50.core.exceptions import DatasetImportError
from binance50.ml.datasets.storage import ml_dataset_to_storage_frames

def import_ml_dataset_result(
    storage_manager: Any,
    result: MLDatasetBuildResult,
    config: AppConfig,
    overwrite: bool = False,
) -> None:
    if not result.success or result.dataset_df is None or result.manifest is None:
        raise DatasetImportError("Cannot import failed or empty ML dataset result")

    if result.quality_report.status != "passed" and result.quality_report.status != "warnings":
         raise DatasetImportError("Cannot import dataset failing quality checks")

    if result.leakage_report.status != "clean" and result.leakage_report.status != "warnings":
        raise DatasetImportError("Cannot import dataset with critical leakage issues")

    for feature_col in result.manifest.feature_columns:
        if any(w in feature_col.lower() for w in ["label", "target", "future"]):
            raise DatasetImportError("Feature dataframe contains forbidden feature columns")

    frames = ml_dataset_to_storage_frames(result)
    for dataset_name, df in frames.items():
        if df is not None and not df.empty:
            storage_manager.append_dataframe(dataset_name, df)


def import_ml_training_result(result: Any, config: AppConfig) -> Any:
    # Validate rules
    if not result.success:
        raise ValueError("Cannot import failed run")
    if not result.dataset_manifest:
        raise ValueError("Cannot import without dataset manifest link")

    for m in result.model_results:
        if not m.model_card:
            raise ValueError("Cannot import without model card")
        if hasattr(m, "prediction_intent") and getattr(m, "prediction_intent") in ["live", "paper", "serving"]:
            raise ValueError("Cannot import models with live/paper/serving intent")

    return {"status": "imported", "run_id": result.run_id}


def import_ml_inference_result(result: Any, config: AppConfig) -> Any:
    if not getattr(result, "success", False):
        raise ValueError("Cannot import failed run")

    quality_report = getattr(result, "quality_report", None)
    if quality_report and getattr(quality_report, "status", "") == "failed":
        raise ValueError("Cannot import run failing quality checks")

    model_load_report = getattr(result, "model_load_report", None)
    if model_load_report and not getattr(model_load_report, "hash_verified", False):
        raise ValueError("Cannot import run without verified artifact hash")

    sandbox_outputs = getattr(result, "sandbox_outputs", {})
    if not getattr(config.ml_inference.sandbox_integration, "write_to_signal_engine_forbidden", True):
        raise ValueError("Sandbox outputs cannot be imported as production signals")

    # This dummy function simulates the behavior described in requirements
    class DatasetManifest:
        pass

    return DatasetManifest()
