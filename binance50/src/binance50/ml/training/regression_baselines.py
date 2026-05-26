from typing import Any
from binance50.config.models import AppConfig

def validate_regression_skeleton_config(config: AppConfig) -> None:
    if not config.ml_training.task.regression_default_enabled:
        pass # Expected disabled by default

def build_dummy_regressor(config: AppConfig) -> Any:
    from sklearn.dummy import DummyRegressor
    return DummyRegressor(strategy="mean")

def build_ridge_regressor_skeleton(config: AppConfig) -> Any:
    from sklearn.linear_model import Ridge
    return Ridge(random_state=config.ml_training.models.random_state)

def build_random_forest_regressor_skeleton(config: AppConfig) -> Any:
    from sklearn.ensemble import RandomForestRegressor
    return RandomForestRegressor(
        n_estimators=100,
        max_depth=6,
        random_state=config.ml_training.models.random_state,
        n_jobs=config.ml_training.models.n_jobs
    )

def fit_regressor_skeleton(estimator: Any, X_train: Any, y_train: Any, config: AppConfig) -> Any:
    estimator.fit(X_train, y_train)
    return estimator
