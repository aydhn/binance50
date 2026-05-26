from typing import Any
import hashlib
from binance50.config.models import AppConfig

def compute_ml_training_input_hash(dataset_manifest: Any, config: AppConfig) -> str:
    return hashlib.sha256(str(dataset_manifest).encode()).hexdigest()

def compute_model_config_hash(model_name: str, config: AppConfig) -> str:
    cfg = getattr(config.ml_training.models, model_name, None)
    return hashlib.sha256(str(cfg).encode()).hexdigest()

def compute_training_run_hash(result: Any) -> str:
    return hashlib.sha256(result.run_id.encode()).hexdigest()

def compute_model_result_hash(model_result: Any) -> str:
    return hashlib.sha256(model_result.model_id.encode()).hexdigest()

def build_ml_training_reproducibility_report(result: Any, config: AppConfig) -> dict:
    return {"hash": compute_training_run_hash(result)}

def assert_ml_training_reproducible(result_a: Any, result_b: Any) -> None:
    if compute_training_run_hash(result_a) != compute_training_run_hash(result_b):
        raise ValueError("Results are not reproducible")
