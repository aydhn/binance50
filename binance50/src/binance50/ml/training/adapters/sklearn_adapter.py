from typing import Any, Dict, Optional
import sys

class SklearnTrainingAdapter:
    def __init__(self):
        try:
            import sklearn
            self.sklearn_available = True
            self.sklearn_version = sklearn.__version__
        except ImportError:
            self.sklearn_available = False
            self.sklearn_version = "unknown"

    def availability_report(self) -> Dict[str, Any]:
        return {
            "sklearn_available": self.sklearn_available,
            "sklearn_version": self.sklearn_version,
            "python_version": sys.version,
            "can_train": self.sklearn_available
        }

    def get_sklearn_version(self) -> str:
        return self.sklearn_version

    def validate_environment(self) -> Dict[str, Any]:
        return self.availability_report()

    def fit(self, estimator: Any, X: Any, y: Any) -> Any:
        if not self.sklearn_available:
            raise RuntimeError("scikit-learn is not available")
        return estimator.fit(X, y)

    def predict(self, estimator: Any, X: Any) -> Any:
        if not self.sklearn_available:
            raise RuntimeError("scikit-learn is not available")
        return estimator.predict(X)

    def predict_proba(self, estimator: Any, X: Any) -> Any:
        if not self.sklearn_available:
            raise RuntimeError("scikit-learn is not available")
        if hasattr(estimator, "predict_proba"):
            return estimator.predict_proba(X)
        raise RuntimeError(f"Estimator {type(estimator).__name__} does not support predict_proba")

    def save_with_joblib(self, estimator: Any, path: str) -> None:
        if not self.sklearn_available:
            raise RuntimeError("scikit-learn is not available")
        try:
            import joblib
            joblib.dump(estimator, path)
        except ImportError:
            raise RuntimeError("joblib is not available")
