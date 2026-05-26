import pytest
from binance50.safety.ml_model_leakage_guard import (
    assert_training_features_leakage_free, assert_dataset_manifest_leakage_free
)

def test_ml_model_leakage_guard():
    assert_training_features_leakage_free(["f1", "f2"])

    with pytest.raises(ValueError, match="Leakage suspected"):
        assert_training_features_leakage_free(["f1", "label_1"])

    with pytest.raises(ValueError, match="Leakage suspected"):
        assert_training_features_leakage_free(["f1", "target_price"])

    with pytest.raises(ValueError, match="Leakage suspected"):
        assert_training_features_leakage_free(["f1", "future_return"])

    assert_dataset_manifest_leakage_free({"leakage_status": "clean"})

    with pytest.raises(ValueError, match="Dataset is not leakage free"):
        assert_dataset_manifest_leakage_free({"leakage_status": "warning"})
