import hashlib
import json
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindow, WalkForwardWindowResult


def compute_walkforward_input_hash(df: pd.DataFrame, config: AppConfig, search_space: Any) -> str:
    # Hash data properties
    data_str = f"len:{len(df)}|cols:{','.join(df.columns)}"
    if "open_time" in df.columns:
        data_str += f"|start:{df['open_time'].min()}|end:{df['open_time'].max()}"

    config_hash = hashlib.sha256(
        json.dumps(config.model_dump(), sort_keys=True, default=str).encode()
    ).hexdigest()

    # Hash search space
    space_str = json.dumps(search_space, sort_keys=True, default=str) if search_space else ""

    combined = f"{data_str}|{config_hash}|{space_str}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_window_hash(window: WalkForwardWindow) -> str:
    win_str = json.dumps(window.model_dump(), sort_keys=True, default=str)
    return hashlib.sha256(win_str.encode("utf-8")).hexdigest()


def compute_window_result_hash(window_result: WalkForwardWindowResult) -> str:
    # Hash the core outputs (selected params, oos metrics)
    data = {
        "window_id": window_result.window_id,
        "status": window_result.status,
        "selected_params": window_result.selected_parameter_set,
        "oos_metrics": window_result.oos_report.get("metrics", {})
        if window_result.oos_report
        else {},
    }
    res_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(res_str.encode("utf-8")).hexdigest()


def compute_walkforward_output_hash(result: Any) -> str:
    if not hasattr(result, "window_results"):
        return "invalid"

    win_hashes = [compute_window_result_hash(r) for r in result.window_results.values()]
    win_hashes.sort()

    combined = "|".join(win_hashes)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def build_walkforward_reproducibility_report(result: Any, config: AppConfig) -> dict[str, Any]:
    metadata = getattr(result, "metadata", {})
    return {
        "input_hash": metadata.get("input_hash", ""),
        "config_hash": metadata.get("config_hash", ""),
        "window_plan_hash": metadata.get("window_plan_hash", ""),
        "output_hash": metadata.get("output_hash", ""),
        "deterministic_mode": config.walkforward.mode.deterministic,
    }


def assert_walkforward_reproducible(result_a: Any, result_b: Any) -> None:
    hash_a = getattr(result_a, "metadata", {}).get("output_hash")
    hash_b = getattr(result_b, "metadata", {}).get("output_hash")

    if not hash_a or not hash_b:
        raise ValueError("Cannot verify reproducibility: missing hashes")

    if hash_a != hash_b:
        raise ValueError(f"Reproducibility failed: {hash_a} != {hash_b}")
