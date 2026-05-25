import hashlib
import json
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunResult, OptimizationTrial


def compute_optimization_input_hash(
    df: pd.DataFrame | None, search_space: list[Any], config: AppConfig
) -> str:
    # Hash data
    data_hash = "no_data"
    if df is not None and not df.empty:
        # Simple hash of index and some shape for reproducibility check
        data_info = f"{len(df)}_{df.index[0]}_{df.index[-1]}"
        data_hash = hashlib.sha256(data_info.encode()).hexdigest()

    # Hash config
    config_dump = config.model_dump(mode="json")
    config_str = json.dumps(config_dump, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode()).hexdigest()

    # Hash search space
    space_dicts = [s.model_dump(mode="json") for s in search_space]
    space_str = json.dumps(space_dicts, sort_keys=True)
    space_hash = hashlib.sha256(space_str.encode()).hexdigest()

    combined = f"{data_hash}_{config_hash}_{space_hash}_{config.optimizer.mode.random_seed}"
    return hashlib.sha256(combined.encode()).hexdigest()


def compute_trial_hash(trial: OptimizationTrial) -> str:
    # Base hash on parameters and inputs
    param_hash = trial.parameter_set.hash
    # We add run_id as well
    combined = f"{param_hash}_{trial.run_id}"
    return hashlib.sha256(combined.encode()).hexdigest()


def compute_optimization_output_hash(result: OptimizationRunResult) -> str:
    trial_hashes = [t.metadata.get("hash", compute_trial_hash(t)) for t in result.trials]
    trial_hashes.sort()

    combined = "_".join(trial_hashes)
    return hashlib.sha256(combined.encode()).hexdigest()


def build_optimizer_reproducibility_report(
    result: OptimizationRunResult, config: AppConfig
) -> dict:
    return {
        "run_id": result.run_id,
        "input_hash": result.metadata.get("input_hash"),
        "search_space_hash": result.metadata.get("search_space_hash"),
        "config_hash": result.metadata.get("config_hash"),
        "output_hash": compute_optimization_output_hash(result),
        "random_seed": config.optimizer.mode.random_seed,
        "deterministic_mode": config.optimizer.mode.deterministic,
    }


def assert_reproducible_run(
    result_a: OptimizationRunResult, result_b: OptimizationRunResult
) -> None:
    hash_a = compute_optimization_output_hash(result_a)
    hash_b = compute_optimization_output_hash(result_b)

    if hash_a != hash_b:
        raise ValueError(f"Runs are not reproducible: {hash_a} != {hash_b}")
