import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.training.classifier_baselines import (
    build_dummy_classifier, build_logistic_regression_classifier,
    build_random_forest_classifier, build_hist_gradient_boosting_classifier,
    validate_classifier_supports_predict_proba, fit_classifier
)

def test_classifier_baselines():
    config = AppConfig()
    dc = build_dummy_classifier(config)
    lr = build_logistic_regression_classifier(config)
    rf = build_random_forest_classifier(config)
    hgb = build_hist_gradient_boosting_classifier(config)

    assert validate_classifier_supports_predict_proba(dc)
    assert validate_classifier_supports_predict_proba(lr)
    assert validate_classifier_supports_predict_proba(rf)
    assert validate_classifier_supports_predict_proba(hgb)

    X = pd.DataFrame({"A": [1, 2, 3, 4]})
    y = pd.Series([0, 1, 0, 1])

    fit_classifier(dc, X, y, config)
    assert hasattr(dc, "classes_")
