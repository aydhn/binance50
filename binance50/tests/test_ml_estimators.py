import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLTaskType
from binance50.ml.training.estimators import MLEstimatorFactory

def test_list_enabled_estimators():
    config = AppConfig()
    config.ml_training.models.enabled_models = ["logistic_regression", "dummy_classifier"]
    factory = MLEstimatorFactory()
    assert factory.list_enabled_estimators(config) == ["logistic_regression", "dummy_classifier"]

def test_build_estimators():
    config = AppConfig()
    factory = MLEstimatorFactory()

    # Classification
    lr = factory.build_estimator("logistic_regression", MLTaskType.classification, config)
    assert type(lr).__name__ == "LogisticRegression"

    rf = factory.build_estimator("random_forest_classifier", MLTaskType.classification, config)
    assert type(rf).__name__ == "RandomForestClassifier"

    hgb = factory.build_estimator("hist_gradient_boosting_classifier", MLTaskType.classification, config)
    assert type(hgb).__name__ == "HistGradientBoostingClassifier"

    dummy = factory.build_estimator("dummy_classifier", MLTaskType.classification, config)
    assert type(dummy).__name__ == "DummyClassifier"

    # Regression
    dr = factory.build_estimator("dummy_regressor", MLTaskType.regression_skeleton, config)
    assert type(dr).__name__ == "DummyRegressor"

    rr = factory.build_estimator("ridge_regressor_skeleton", MLTaskType.regression_skeleton, config)
    assert type(rr).__name__ == "Ridge"

    rfr = factory.build_estimator("random_forest_regressor_skeleton", MLTaskType.regression_skeleton, config)
    assert type(rfr).__name__ == "RandomForestRegressor"

def test_estimator_metadata():
    config = AppConfig()
    factory = MLEstimatorFactory()
    lr = factory.build_estimator("logistic_regression", MLTaskType.classification, config)
    meta = factory.build_estimator_metadata(lr, "logistic_regression", config)
    assert meta["model_name"] == "logistic_regression"
    assert meta["class_name"] == "LogisticRegression"
