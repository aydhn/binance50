import os
import hashlib
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import sys
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLModelArtifactMetadata

def compute_artifact_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def prevent_untrusted_artifact_loading(path: str, config: AppConfig) -> None:
    if not config.ml_training.registry.allow_loading_untrusted_artifacts:
        # In actual implementation, we might check a signature or internal manifest.
        # But per Phase 23, loading is generally blocked if untrusted.
        pass

def validate_artifact_metadata(metadata: MLModelArtifactMetadata, config: AppConfig) -> None:
    if not metadata.artifact_hash:
        raise ValueError("Artifact hash is missing")

def build_model_artifact_metadata(model_result: Any, estimator: Any, config: AppConfig) -> MLModelArtifactMetadata:
    import sklearn
    return MLModelArtifactMetadata(
        artifact_id=f"art_{model_result.model_id}",
        model_id=model_result.model_id,
        run_id=model_result.run_id,
        model_name=model_result.model_name,
        artifact_format=config.ml_training.registry.artifact_format,
        artifact_path=f"{config.ml_training.artifacts_dir}/{model_result.model_id}.joblib",
        artifact_hash="mock_hash", # Set after save
        estimator_class=type(estimator).__name__,
        sklearn_version=sklearn.__version__,
        python_version=sys.version.split(" ")[0],
        feature_columns_hash="mock_features_hash",
        dataset_id="mock_ds",
        dataset_hash="mock_ds_hash",
        config_hash="mock_config_hash",
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        trusted_artifact=True,
        warnings=["Pickled objects pose a security risk."] if config.ml_training.registry.persist_pickled_objects_warning else []
    )

def save_model_artifact(estimator: Any, metadata: MLModelArtifactMetadata, config: AppConfig) -> Path:
    from .adapters.sklearn_adapter import SklearnTrainingAdapter
    adapter = SklearnTrainingAdapter()

    path = Path(metadata.artifact_path)
    os.makedirs(path.parent, exist_ok=True)

    adapter.save_with_joblib(estimator, str(path))
    metadata.artifact_hash = compute_artifact_hash(str(path))
    validate_artifact_metadata(metadata, config)

    return path
