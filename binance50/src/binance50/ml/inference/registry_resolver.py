from typing import Any, Dict
from binance50.config.models import AppConfig
from binance50.core.exceptions import MLRegistryResolveError

class MLInferenceRegistryResolver:
    def __init__(self, registry_manager: Any = None):
        self.registry_manager = registry_manager

    def resolve_model(self, model_id: str, config: AppConfig) -> Any:
        if not self.registry_manager:
            raise MLRegistryResolveError("Registry manager not provided")
        model_result = self.registry_manager.get_model(model_id)
        if not model_result:
            raise MLRegistryResolveError(f"Model {model_id} not found in registry")
        self.validate_model_registry_entry(model_result, config)
        return model_result

    def resolve_latest_candidate_model(self, symbol: str, market_scope: str, interval: str, config: AppConfig) -> Any:
        if not self.registry_manager:
            raise MLRegistryResolveError("Registry manager not provided")
        # Dummy lookup logic for test purposes
        return None

    def resolve_dataset_for_model(self, model_result: Any, config: AppConfig) -> Any:
        # Dummy logic
        return None

    def validate_model_registry_entry(self, model_result: Any, config: AppConfig) -> None:
        if config.ml_inference.model_source.require_model_card and not getattr(model_result, "model_card", None):
            raise MLRegistryResolveError("Model card is required but missing")
        if config.ml_inference.model_source.require_artifact_metadata and not getattr(model_result, "artifact_metadata", None):
            raise MLRegistryResolveError("Artifact metadata is required but missing")
        if config.ml_inference.model_source.require_dataset_manifest_link and not getattr(model_result, "dataset_manifest", None):
            raise MLRegistryResolveError("Dataset manifest link is required but missing")

    def build_resolver_report(self, model_result: Any) -> Dict[str, Any]:
        return {
            "model_id": getattr(model_result, "run_id", "unknown"),
            "resolved": True,
        }
