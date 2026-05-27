import pytest
from pathlib import Path
from binance50.config.models import AppConfig
from binance50.ml.inference.artifact_loader import TrustedMLArtifactLoader
from binance50.core.exceptions import MLArtifactTrustError, MLArtifactHashMismatchError

class MockModelResult:
    def __init__(self, metadata_present=True):
        self.run_id = "test"
        if metadata_present:
            self.artifact_metadata = {"test": "data"}

def test_verify_artifact_metadata():
    config = AppConfig()
    loader = TrustedMLArtifactLoader()
    report = loader.verify_artifact_metadata(MockModelResult(), config)
    assert report.trusted_artifact is True

def test_verify_artifact_metadata_missing():
    config = AppConfig()
    loader = TrustedMLArtifactLoader()
    with pytest.raises(MLArtifactTrustError, match="Missing artifact metadata"):
        loader.verify_artifact_metadata(MockModelResult(metadata_present=False), config)

def test_verify_artifact_hash(tmp_path):
    loader = TrustedMLArtifactLoader()
    file_path = tmp_path / "test.bin"
    file_path.write_bytes(b"test data")

    import hashlib
    h = hashlib.sha256(b"test data").hexdigest()

    assert loader.verify_artifact_hash(file_path, h) == h

def test_verify_artifact_hash_mismatch(tmp_path):
    loader = TrustedMLArtifactLoader()
    file_path = tmp_path / "test.bin"
    file_path.write_bytes(b"test data")

    with pytest.raises(MLArtifactHashMismatchError, match="Expected bad_hash"):
        loader.verify_artifact_hash(file_path, "bad_hash")

def test_block_untrusted_artifact():
    config = AppConfig()
    loader = TrustedMLArtifactLoader()
    with pytest.raises(MLArtifactTrustError, match="blocked"):
        loader.block_untrusted_artifact(Path("fake"), config)
