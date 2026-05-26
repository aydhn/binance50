import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.model_artifacts import (
    build_model_artifact_metadata, prevent_untrusted_artifact_loading,
    validate_artifact_metadata
)
from binance50.ml.training.models import MLModelArtifactMetadata

class MockEstimator:
    pass

class MockResult:
    model_id = "123"
    run_id = "456"
    model_name = "test_model"

def test_build_model_artifact_metadata():
    config = AppConfig()
    res = MockResult()
    est = MockEstimator()
    meta = build_model_artifact_metadata(res, est, config)
    assert meta.model_id == "123"
    assert meta.artifact_format == "joblib"
    assert meta.trusted_artifact is True

def test_prevent_untrusted_artifact_loading():
    config = AppConfig()
    prevent_untrusted_artifact_loading("path", config) # Should pass safely in phase 23

def test_validate_artifact_metadata():
    config = AppConfig()
    meta = MLModelArtifactMetadata(
        artifact_id="1", model_id="2", run_id="3", model_name="4", artifact_format="j",
        artifact_path="p", artifact_hash="", estimator_class="c", sklearn_version="s",
        python_version="p", feature_columns_hash="f", dataset_id="d", dataset_hash="d",
        config_hash="c", created_at_utc="c", trusted_artifact=True
    )
    with pytest.raises(ValueError, match="Artifact hash is missing"):
        validate_artifact_metadata(meta, config)
