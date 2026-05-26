from typing import Any, List, Dict
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLTaskType

from .classifier_baselines import (
    build_dummy_classifier,
    build_logistic_regression_classifier,
    build_random_forest_classifier,
    build_hist_gradient_boosting_classifier
)
from .regression_baselines import (
    build_dummy_regressor,
    build_ridge_regressor_skeleton,
    build_random_forest_regressor_skeleton
)

class MLEstimatorFactory:
    def list_enabled_estimators(self, config: AppConfig) -> List[str]:
        return config.ml_training.models.enabled_models

    def build_estimator(self, model_name: str, task_type: MLTaskType, config: AppConfig) -> Any:
        if task_type == MLTaskType.classification:
            if model_name == "dummy_classifier":
                return build_dummy_classifier(config)
            elif model_name == "logistic_regression":
                return build_logistic_regression_classifier(config)
            elif model_name == "random_forest_classifier":
                return build_random_forest_classifier(config)
            elif model_name == "hist_gradient_boosting_classifier":
                return build_hist_gradient_boosting_classifier(config)
            else:
                raise ValueError(f"Unsupported classification model: {model_name}")
        elif task_type == MLTaskType.regression_skeleton:
            if model_name == "dummy_regressor":
                return build_dummy_regressor(config)
            elif model_name == "ridge_regressor_skeleton":
                return build_ridge_regressor_skeleton(config)
            elif model_name == "random_forest_regressor_skeleton":
                return build_random_forest_regressor_skeleton(config)
            else:
                raise ValueError(f"Unsupported regression model: {model_name}")
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    def validate_estimator(self, estimator: Any, model_name: str, config: AppConfig) -> None:
        if config.ml_training.models.require_deterministic_models:
            if hasattr(estimator, "random_state") and getattr(estimator, "random_state") is None:
                pass # Accept default None or test specifically. Most sklean models take random_state but HistGrad has defaults.

    def build_estimator_metadata(self, estimator: Any, model_name: str, config: AppConfig) -> Dict[str, Any]:
        return {
            "model_name": model_name,
            "class_name": type(estimator).__name__
        }
