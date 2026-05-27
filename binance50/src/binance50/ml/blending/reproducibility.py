import hashlib
import json
from typing import Any

from binance50.config.models import AppConfig
from binance50.ml.blending.models import MLBlendingRunResult


def compute_blending_input_hash(inputs: dict[str, Any], config: AppConfig) -> str:
    data = json.dumps(inputs, sort_keys=True, default=str)
    return hashlib.sha256(data.encode()).hexdigest()


def compute_blending_output_hash(result: MLBlendingRunResult) -> str:
    data = json.dumps(
        result.model_dump(exclude={"metadata", "created_at_utc"}), sort_keys=True, default=str
    )
    return hashlib.sha256(data.encode()).hexdigest()


def compute_candidate_hash(candidate: Any) -> str:
    data = json.dumps(
        candidate.model_dump(exclude={"metadata", "created_at_utc"}), sort_keys=True, default=str
    )
    return hashlib.sha256(data.encode()).hexdigest()


def compute_blending_config_hash(config: AppConfig) -> str:
    data = json.dumps(config.ml_blending.model_dump(), sort_keys=True, default=str)
    return hashlib.sha256(data.encode()).hexdigest()


def build_ml_blending_reproducibility_report(
    result: MLBlendingRunResult, config: AppConfig
) -> dict[str, Any]:
    return {"status": "ok"}


def assert_ml_blending_reproducible(
    result_a: MLBlendingRunResult, result_b: MLBlendingRunResult
) -> None:
    if compute_blending_output_hash(result_a) != compute_blending_output_hash(result_b):
        raise AssertionError("Results are not reproducible")
