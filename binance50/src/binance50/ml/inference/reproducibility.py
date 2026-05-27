import hashlib
import json
from typing import Any, Dict, List
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow, MLInferenceRunResult

def compute_ml_inference_input_hash(model_result: Any, dataset_result: Any, config: AppConfig) -> str:
    # Dummy mock
    s = str(getattr(model_result, "run_id", "1")) + str(getattr(dataset_result, "dataset_id", "2"))
    return hashlib.sha256(s.encode()).hexdigest()

def compute_prediction_hash(predictions: List[MLPredictionRow]) -> str:
    # Dummy mock
    s = "".join([str(p.prediction_id) + str(p.predicted_label) for p in predictions])
    return hashlib.sha256(s.encode()).hexdigest()

def compute_inference_output_hash(result: MLInferenceRunResult) -> str:
    # Dummy mock
    s = compute_prediction_hash(result.predictions)
    return hashlib.sha256(s.encode()).hexdigest()

def compute_inference_config_hash(config: AppConfig) -> str:
    s = json.dumps(config.ml_inference.model_dump(), sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def build_ml_inference_reproducibility_report(result: MLInferenceRunResult, config: AppConfig) -> Dict[str, Any]:
    return {
        "input_hash": "dummy",
        "output_hash": compute_inference_output_hash(result),
        "config_hash": compute_inference_config_hash(config)
    }

def assert_ml_inference_reproducible(result_a: MLInferenceRunResult, result_b: MLInferenceRunResult) -> None:
    pass
