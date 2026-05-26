import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.training.regression_baselines import (
    build_dummy_regressor, build_ridge_regressor_skeleton,
    build_random_forest_regressor_skeleton, fit_regressor_skeleton,
    validate_regression_skeleton_config
)

def test_regression_baselines():
    config = AppConfig()
    validate_regression_skeleton_config(config)

    dr = build_dummy_regressor(config)
    rr = build_ridge_regressor_skeleton(config)
    rf = build_random_forest_regressor_skeleton(config)

    X = pd.DataFrame({"A": [1.0, 2.0, 3.0, 4.0]})
    y = pd.Series([1.1, 2.1, 3.1, 4.1])

    fit_regressor_skeleton(dr, X, y, config)
    assert hasattr(dr, "constant_")
