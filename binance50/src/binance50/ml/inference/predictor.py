from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow, MLInferenceRunRequest, MLInferenceIntent
from binance50.ml.inference.adapters.sklearn_inference_adapter import SklearnInferenceAdapter
from binance50.ml.inference.feature_schema import compute_feature_schema_hash
from binance50.core.exceptions import MLPredictionError

class MLBatchPredictor:
    def __init__(self, config: AppConfig, artifact_loader: Any = None, inference_adapter: Any = None, preprocessor: Any = None):
        self.config = config
        self.artifact_loader = artifact_loader
        self.inference_adapter = inference_adapter or SklearnInferenceAdapter()
        self.preprocessor = preprocessor

    def batch_iter(self, X: pd.DataFrame, batch_size: int):
        for i in range(0, len(X), batch_size):
            yield X.iloc[i:i + batch_size], i

    def predict_batch(self, estimator: Any, X: pd.DataFrame, row_metadata: List[Dict[str, Any]], model_result: Any, config: AppConfig) -> List[MLPredictionRow]:
        pred = self.inference_adapter.predict(estimator, X)
        proba = None
        if config.ml_inference.prediction.require_predict_proba_if_classifier_supports:
            proba = self.inference_adapter.predict_proba(estimator, X)

        decision_score = None
        if config.ml_inference.prediction.allow_decision_function:
            decision_score = self.inference_adapter.decision_function(estimator, X)

        self.inference_adapter.validate_prediction_shapes(pred, proba, X)

        feature_schema_hash = compute_feature_schema_hash(list(X.columns))

        rows = []
        for i in range(len(X)):
            meta = row_metadata[i]

            prob_dict = None
            max_prob = None
            if proba is not None:
                prob_dict = {str(j): float(p) for j, p in enumerate(proba[i])}
                max_prob = float(np.max(proba[i]))

            dec_score = float(decision_score[i]) if decision_score is not None else None

            row = MLPredictionRow(
                prediction_id=f"pred_{meta.get('index', i)}",
                model_id=getattr(model_result, "run_id", "unknown"),
                dataset_id="dataset",
                symbol=meta.get("symbol", "unknown"),
                market_scope=meta.get("market_scope", "spot"),
                interval=meta.get("interval", "1m"),
                open_time=meta.get("open_time", "now"),
                predicted_label=str(pred[i]),
                predicted_class_index=int(pred[i]) if isinstance(pred[i], (int, np.integer)) else 0,
                probabilities=prob_dict,
                max_probability=max_prob,
                confidence=max_prob,
                decision_score=dec_score,
                prediction_intent=MLInferenceIntent.RESEARCH_ONLY,
                feature_schema_hash=feature_schema_hash
            )
            rows.append(row)
        return rows

    def run_batch_prediction(self, model_result: Any, dataset_result: Any, split_name: str, request: MLInferenceRunRequest) -> List[MLPredictionRow]:
        # Dummy mock to be used in integration test or similar scenarios
        return []

    def validate_predictions(self, predictions: List[MLPredictionRow], config: AppConfig) -> None:
        if not predictions and config.ml_inference.prediction.require_predict_output:
            raise MLPredictionError("No predictions generated")

        for p in predictions:
            if p.prediction_intent not in (MLInferenceIntent.RESEARCH_ONLY, MLInferenceIntent.NO_ORDER):
                raise MLPredictionError(f"Invalid prediction intent: {p.prediction_intent}")
            if hasattr(p, "order_id") or hasattr(p, "quantity"):
                raise MLPredictionError("Execution fields detected in prediction output")
