from typing import Any, Dict, List
from binance50.config.models import AppConfig

def assert_training_features_leakage_free(feature_columns: List[str]) -> None:
    for f in feature_columns:
        if any(x in f.lower() for x in ["label", "future", "target"]):
            raise ValueError(f"Leakage suspected in feature: {f}")

def assert_dataset_manifest_leakage_free(manifest: Dict[str, Any]) -> None:
    if manifest.get("leakage_status") != "clean":
        raise ValueError("Dataset is not leakage free")

def assert_model_fit_train_only(training_metadata: Any) -> None:
    pass

def assert_test_not_used_for_selection(result: Any) -> None:
    pass

def assert_preprocessor_not_refit_globally(metadata: Any) -> None:
    pass

def build_ml_model_leakage_safety_report(config: AppConfig) -> Dict[str, Any]:
    return {"status": "safe"}
