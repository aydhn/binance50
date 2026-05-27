import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.registry_resolver import MLInferenceRegistryResolver
from binance50.core.exceptions import MLRegistryResolveError

class MockRegistryManager:
    def get_model(self, model_id):
        if model_id == "good":
            class MockModel:
                run_id = "good"
                model_card = {"mock": "data"} # Pydantic expects a boolean-like check, empty dict is falsy in some contexts if not careful, use true object
                artifact_metadata = {"mock": "data"}
                dataset_manifest = "link"
            return MockModel()
        elif model_id == "missing_card":
            class MockModel:
                run_id = "missing_card"
                artifact_metadata = {"mock": "data"}
                dataset_manifest = "link"
            return MockModel()
        return None

def test_resolve_model_success():
    config = AppConfig()
    resolver = MLInferenceRegistryResolver(registry_manager=MockRegistryManager())
    model = resolver.resolve_model("good", config)
    assert model.run_id == "good"

def test_resolve_model_not_found():
    config = AppConfig()
    resolver = MLInferenceRegistryResolver(registry_manager=MockRegistryManager())
    with pytest.raises(MLRegistryResolveError, match="not found"):
        resolver.resolve_model("bad", config)

def test_resolve_model_missing_card():
    config = AppConfig()
    resolver = MLInferenceRegistryResolver(registry_manager=MockRegistryManager())
    with pytest.raises(MLRegistryResolveError, match="Model card is required"):
        resolver.resolve_model("missing_card", config)
