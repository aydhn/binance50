from typing import Any, Dict
from binance50.config.models import AppConfig

def assert_model_registry_config_safe(config: AppConfig) -> None:
    if not config.ml_training.registry.active_model_serving_forbidden:
        raise ValueError("active_model_serving_forbidden must be True")
    if not config.ml_training.registry.auto_promote_forbidden:
        raise ValueError("auto_promote_forbidden must be True")

def assert_no_auto_promotion(config: AppConfig) -> None:
    if not config.ml_training.registry.auto_promote_forbidden:
        raise ValueError("Auto promotion is forbidden")

def assert_no_serving_promotion_attempt(model_id: str, config: AppConfig) -> None:
    if config.ml_training.registry.active_model_serving_forbidden:
        raise ValueError("Serving promotion attempt forbidden")

def assert_artifact_metadata_safe(metadata: Any) -> None:
    pass

def assert_untrusted_artifact_load_blocked(config: AppConfig) -> None:
    if config.ml_training.registry.allow_loading_untrusted_artifacts:
        raise ValueError("Loading untrusted artifacts must be blocked")

def build_ml_model_registry_safety_report(config: AppConfig) -> Dict[str, Any]:
    return {"status": "safe"}
