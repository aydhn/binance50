import pytest
from binance50.config.models import AppConfig
from binance50.ml.inference.feature_schema import (
    build_expected_feature_schema,
    build_actual_feature_schema,
    compute_feature_schema_hash,
    compare_feature_schema,
    validate_feature_schema_for_inference
)
from binance50.core.exceptions import MLFeatureSchemaError

class MockResult:
    def __init__(self, cols):
        self.feature_schema = {"columns": cols, "dtypes": {}}

def test_schema_hash_deterministic():
    h1 = compute_feature_schema_hash(["a", "b"])
    h2 = compute_feature_schema_hash(["a", "b"])
    assert h1 == h2

def test_compare_schema_exact_match():
    config = AppConfig()
    exp = build_expected_feature_schema(MockResult(["f1", "f2"]))
    act = build_actual_feature_schema(MockResult(["f1", "f2"]))

    report = compare_feature_schema(exp, act, config)
    assert report.passed is True
    assert report.exact_columns_match is True
    assert report.exact_order_match is True

def test_compare_schema_order_mismatch():
    config = AppConfig()
    exp = build_expected_feature_schema(MockResult(["f1", "f2"]))
    act = build_actual_feature_schema(MockResult(["f2", "f1"]))

    report = compare_feature_schema(exp, act, config)
    assert report.exact_columns_match is True
    assert report.exact_order_match is False
    assert report.passed is False

def test_validate_feature_schema_fail():
    config = AppConfig()
    exp = build_expected_feature_schema(MockResult(["f1", "f2"]))
    act = build_actual_feature_schema(MockResult(["f1"]))

    report = compare_feature_schema(exp, act, config)
    with pytest.raises(MLFeatureSchemaError, match="Missing features: \\['f2'\\]"):
        validate_feature_schema_for_inference(report, config)
