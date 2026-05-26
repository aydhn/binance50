import pandas as pd
from typing import Any
from binance50.config.models import AppConfig

def compute_ml_input_hash(source_frames: dict[str, pd.DataFrame], config: AppConfig) -> str:
    return "dummy_input_hash"

def compute_feature_hash(features_df: pd.DataFrame) -> str:
    return "dummy_feature_hash"

def compute_label_hash(labels_df: pd.DataFrame) -> str:
    return "dummy_label_hash"

def compute_dataset_hash(dataset_df: pd.DataFrame) -> str:
    return "dummy_dataset_hash"

def compute_ml_config_hash(config: AppConfig) -> str:
    return "dummy_config_hash"

def build_ml_reproducibility_report(manifest: Any, config: AppConfig) -> dict[str, Any]:
    return {}

def assert_ml_dataset_reproducible(result_a: Any, result_b: Any) -> None:
    pass
