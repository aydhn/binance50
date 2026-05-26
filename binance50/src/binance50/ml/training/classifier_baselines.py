from typing import Any
from binance50.config.models import AppConfig

def build_dummy_classifier(config: AppConfig) -> Any:
    from sklearn.dummy import DummyClassifier
    return DummyClassifier(strategy=config.ml_training.models.dummy_classifier.strategy)

def build_logistic_regression_classifier(config: AppConfig) -> Any:
    from sklearn.linear_model import LogisticRegression
    cfg = config.ml_training.models.logistic_regression
    return LogisticRegression(
        max_iter=cfg.max_iter,
        class_weight=cfg.class_weight,
        solver=cfg.solver,
        C=cfg.C,
        random_state=config.ml_training.models.random_state
    )

def build_random_forest_classifier(config: AppConfig) -> Any:
    from sklearn.ensemble import RandomForestClassifier
    cfg = config.ml_training.models.random_forest_classifier
    return RandomForestClassifier(
        n_estimators=cfg.n_estimators,
        max_depth=cfg.max_depth,
        min_samples_leaf=cfg.min_samples_leaf,
        class_weight=cfg.class_weight,
        random_state=cfg.random_state,
        n_jobs=cfg.n_jobs
    )

def build_hist_gradient_boosting_classifier(config: AppConfig) -> Any:
    from sklearn.ensemble import HistGradientBoostingClassifier
    cfg = config.ml_training.models.hist_gradient_boosting_classifier
    return HistGradientBoostingClassifier(
        max_iter=cfg.max_iter,
        max_leaf_nodes=cfg.max_leaf_nodes,
        learning_rate=cfg.learning_rate,
        l2_regularization=cfg.l2_regularization,
        random_state=cfg.random_state
    )

def validate_classifier_supports_predict_proba(estimator: Any) -> bool:
    return hasattr(estimator, "predict_proba")

def fit_classifier(estimator: Any, X_train: Any, y_train: Any, config: AppConfig) -> Any:
    estimator.fit(X_train, y_train)
    return estimator
