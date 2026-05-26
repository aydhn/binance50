import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLTaskType
from binance50.ml.training.target_builder import (
    detect_single_class, detect_class_imbalance, validate_target,
    infer_class_labels, build_class_weight_report
)

def test_detect_single_class():
    assert detect_single_class(pd.Series([1, 1, 1])) is True
    assert detect_single_class(pd.Series([1, 2, 1])) is False

def test_detect_class_imbalance():
    config = AppConfig()
    config.ml_dataset.quality.max_majority_class_ratio = 0.8
    y = pd.Series([1]*9 + [0]*1) # 90%
    res = detect_class_imbalance(y, config)
    assert bool(res["imbalanced"]) is True
    assert res["max_ratio"] == 0.9

def test_validate_target():
    config = AppConfig()
    y = pd.Series([1, 1])
    with pytest.raises(ValueError, match="Single class found in target"):
        validate_target(y, MLTaskType.classification, config)

def test_build_class_weight_report():
    y = pd.Series([1, 1, 1, 0])
    res = build_class_weight_report(y)
    assert res["counts"][1] == 3
    assert res["counts"][0] == 1
