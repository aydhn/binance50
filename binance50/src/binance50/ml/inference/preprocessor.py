from typing import Any, Dict
import pandas as pd
from binance50.config.models import AppConfig
from binance50.core.exceptions import MLInferencePreprocessingError

class MLInferencePreprocessor:
    def __init__(self):
        self._fit_called = False

    def load_preprocessor_metadata(self, model_result: Any, dataset_result: Any, config: AppConfig) -> Dict[str, Any]:
        metadata = getattr(model_result, "preprocessor_metadata", None)
        if not metadata and config.ml_inference.preprocessing.require_training_preprocessor_metadata:
            raise MLInferencePreprocessingError("Training preprocessor metadata is required")
        return metadata or {}

    def transform_only(self, X: pd.DataFrame, metadata: Dict[str, Any], config: AppConfig) -> pd.DataFrame:
        self.validate_no_fit_called()
        if not config.ml_inference.preprocessing.transform_only:
            raise MLInferencePreprocessingError("transform_only config is False, which is forbidden")

        expected_hash = metadata.get("hash")
        if expected_hash and config.ml_inference.preprocessing.require_preprocessor_hash:
            self.validate_preprocessor_hash(metadata, expected_hash, config)

        # Dummy transform
        return X.copy()

    def validate_no_fit_called(self) -> None:
        if self._fit_called:
            raise MLInferencePreprocessingError("Fit method called during inference")

    def block_fit(self) -> None:
        self._fit_called = True
        raise MLInferencePreprocessingError("Fit attempt detected during inference")

    def validate_preprocessor_hash(self, metadata: Dict[str, Any], expected_hash: str, config: AppConfig) -> None:
        actual_hash = metadata.get("hash")
        if actual_hash != expected_hash:
            raise MLInferencePreprocessingError(f"Preprocessor hash mismatch: expected {expected_hash}, got {actual_hash}")

    def build_preprocessing_inference_report(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "transform_only": True,
            "preprocessor_hash": metadata.get("hash", "unknown"),
        }
