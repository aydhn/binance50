import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.inference.preprocessor import MLInferencePreprocessor
from binance50.core.exceptions import MLInferencePreprocessingError

class MockModelResult:
    def __init__(self, metadata=None):
        self.preprocessor_metadata = metadata

def test_load_preprocessor_metadata():
    config = AppConfig()
    prep = MLInferencePreprocessor()

    with pytest.raises(MLInferencePreprocessingError, match="Training preprocessor metadata is required"):
        prep.load_preprocessor_metadata(MockModelResult(), None, config)

    meta = prep.load_preprocessor_metadata(MockModelResult({"test": "data"}), None, config)
    assert meta == {"test": "data"}

def test_transform_only():
    config = AppConfig()
    prep = MLInferencePreprocessor()
    df = pd.DataFrame({"f1": [1, 2]})

    res = prep.transform_only(df, {"hash": "h1"}, config)
    assert list(res.columns) == ["f1"]

def test_validate_no_fit_called():
    prep = MLInferencePreprocessor()
    prep.validate_no_fit_called()

    with pytest.raises(MLInferencePreprocessingError, match="Fit attempt detected"):
        prep.block_fit()

    with pytest.raises(MLInferencePreprocessingError, match="Fit method called"):
        prep.validate_no_fit_called()

def test_validate_preprocessor_hash():
    config = AppConfig()
    prep = MLInferencePreprocessor()
    prep.validate_preprocessor_hash({"hash": "h1"}, "h1", config)

    with pytest.raises(MLInferencePreprocessingError, match="hash mismatch"):
        prep.validate_preprocessor_hash({"hash": "h2"}, "h1", config)
