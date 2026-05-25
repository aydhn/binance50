from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindow, WalkForwardWindowResult


def validate_walkforward_config(config: AppConfig) -> None:
    # Trigger pydantic validation
    config.walkforward.validate_safety_rules()


def validate_walkforward_input_df(df: pd.DataFrame, config: AppConfig) -> None:
    if df is None or df.empty:
        raise ValueError("Input dataframe cannot be empty")

    # Must have required columns for splits
    if "open_time" not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
        pass  # Warning or soft error depending on system strictness


def validate_walkforward_windows(windows: list[WalkForwardWindow], config: AppConfig) -> None:
    if not windows and config.walkforward.quality.reject_no_windows:
        raise ValueError("No valid walkforward windows could be generated")

    if len(windows) < config.walkforward.mode.min_windows_required:
        pass  # Handle in quality


def validate_window_result(window_result: WalkForwardWindowResult, config: AppConfig) -> None:
    if window_result.status == "failed" and not config.walkforward.mode.continue_on_window_failure:
        raise ValueError(f"Window {window_result.window_id} failed: {window_result.error}")

    if window_result.status == "completed":
        if (
            config.walkforward.quality.reject_missing_best_trial
            and not window_result.selected_parameter_set
        ):
            raise ValueError(
                f"Completed window {window_result.window_id} missing selected parameters"
            )

        if config.walkforward.quality.reject_missing_oos_results and not window_result.oos_report:
            raise ValueError(f"Completed window {window_result.window_id} missing OOS results")


def validate_walkforward_result(result: Any, config: AppConfig) -> None:
    validate_no_live_or_paper_intent(getattr(result, "request", {}))

    # Check if all failed
    if config.walkforward.quality.reject_all_windows_failed:
        if all(r.status == "failed" for r in result.window_results.values()):
            raise ValueError("All walkforward windows failed")

    if config.walkforward.quality.reject_missing_hashes:
        validate_hashes_present(result)


def validate_no_live_or_paper_intent(payload: Any) -> None:
    # Can be a dict or pydantic model
    data = payload if isinstance(payload, dict) else getattr(payload, "__dict__", {})

    if data.get("intent") in ("live", "paper", "real"):
        raise ValueError("Walkforward payload contains live or paper intent")

    if data.get("trading_mode") in ("live", "paper"):
        raise ValueError("Walkforward payload contains live or paper trading mode")


def validate_no_execution_fields(payload: Any) -> None:
    forbidden_keys = [
        "order_id",
        "client_order_id",
        "exchange_order_id",
        "api_key",
        "signature",
        "listenKey",
        "live_order",
        "testnet_order",
        "paper_order",
        "real_order",
        "execution_gateway",
        "quantity",
        "leverage_to_set",  # Explicit execution fields
    ]

    data = payload if isinstance(payload, dict) else getattr(payload, "__dict__", {})

    # Simple top-level check for this phase
    for key in forbidden_keys:
        if key in data:
            raise ValueError(f"Walkforward payload contains forbidden execution field: {key}")


def validate_hashes_present(result: Any) -> None:
    metadata = getattr(result, "metadata", {})
    if (
        not metadata.get("input_hash")
        or not metadata.get("output_hash")
        or not metadata.get("window_plan_hash")
    ):
        raise ValueError("Walkforward result missing required reproducibility hashes")
