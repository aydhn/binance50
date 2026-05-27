from typing import Any, Dict, Optional
import pandas as pd
import numpy as np

class SklearnInferenceAdapter:
    def availability_report(self) -> Dict[str, Any]:
        try:
            import sklearn
            return {"available": True, "version": sklearn.__version__}
        except ImportError:
            return {"available": False}

    def predict(self, estimator: Any, X: pd.DataFrame) -> np.ndarray:
        return estimator.predict(X)

    def predict_proba(self, estimator: Any, X: pd.DataFrame) -> Optional[np.ndarray]:
        if self.supports_predict_proba(estimator):
            return estimator.predict_proba(X)
        return None

    def decision_function(self, estimator: Any, X: pd.DataFrame) -> Optional[np.ndarray]:
        if self.supports_decision_function(estimator):
            return estimator.decision_function(X)
        return None

    def supports_predict_proba(self, estimator: Any) -> bool:
        return hasattr(estimator, "predict_proba") and callable(getattr(estimator, "predict_proba"))

    def supports_decision_function(self, estimator: Any) -> bool:
        return hasattr(estimator, "decision_function") and callable(getattr(estimator, "decision_function"))

    def validate_prediction_shapes(self, pred: np.ndarray, proba: Optional[np.ndarray], X: pd.DataFrame) -> None:
        if len(pred) != len(X):
            raise ValueError(f"Prediction length {len(pred)} does not match input length {len(X)}")

        if proba is not None and len(proba) != len(X):
            raise ValueError(f"Probability length {len(proba)} does not match input length {len(X)}")
