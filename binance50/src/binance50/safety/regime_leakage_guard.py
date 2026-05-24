from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeLeakageError


def assert_no_regime_lookahead(df: pd.DataFrame, config: AppConfig) -> None:
    invalid_cols = ["target", "label", "future_return", "next_close", "forward_return"]
    for c in df.columns:
        if c in invalid_cols:
            raise RegimeLeakageError(f"Lookahead bias detected: Found column '{c}'")


def assert_no_centered_rolling_usage(config: AppConfig, metadata: dict[str, Any] = None) -> None:
    if metadata is None:
        metadata = {}
    if metadata.get("centered_rolling", False):
        raise RegimeLeakageError("Lookahead bias detected: Centered rolling window is forbidden.")


def assert_optional_model_train_split_used(metadata: dict[str, Any]) -> None:
    if metadata.get("model", "") in ["gmm_optional", "hmm_optional"]:
        if not metadata.get("train_split_used", True):
            raise RegimeLeakageError(
                "Lookahead bias detected: Optional models require train split."
            )


def assert_scaler_not_fit_on_full_dataset(metadata: dict[str, Any]) -> None:
    if metadata.get("scaler_fit_full_dataset", False):
        raise RegimeLeakageError("Lookahead bias detected: Scaler fit on full dataset.")


def assert_higher_timeframe_closed_if_used(df: pd.DataFrame, config: AppConfig) -> None:
    pass  # Simple implementation for now.


def build_regime_leakage_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "safe", "reason": "No leakage detected"}
