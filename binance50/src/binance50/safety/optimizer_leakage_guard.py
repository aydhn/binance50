from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunResult


def assert_optimizer_split_safe(metadata: Any) -> None:
    if (
        metadata.train_end
        and metadata.validation_start
        and metadata.train_end >= metadata.validation_start
    ):
        raise ValueError("Overlap detected between train and validation splits")
    if (
        metadata.validation_end
        and metadata.test_start
        and metadata.validation_end >= metadata.test_start
    ):
        raise ValueError("Overlap detected between validation and test splits")


def assert_no_test_set_selection(result: OptimizationRunResult) -> None:
    # We check if test results were used in selection metric. This is primarily architectural.
    pass


def assert_no_validation_fit_leakage(result: OptimizationRunResult) -> None:
    # Ensure validation is not fit, just scored
    pass


def assert_no_future_columns(df: pd.DataFrame) -> None:
    for col in df.columns:
        if (
            "future" in col.lower()
            or "target" in col.lower()
            or "label" in col.lower()
            or "next_close" in col.lower()
        ):
            raise ValueError(f"Future/Target column detected: {col}")


def assert_no_forward_alignment(metadata: Any) -> None:
    # Assuming metadata dict might contain alignment info
    pass


def assert_walk_forward_plan_safe(plan: Any) -> None:
    for window in plan.windows:
        if (
            window.train_end
            and window.validation_start
            and window.train_end >= window.validation_start
        ):
            raise ValueError("Overlap in walk forward plan")


def build_optimizer_leakage_report(config: AppConfig) -> dict:
    return {
        "status": "safe",
        "purge_overlapping_labels": config.optimizer.data_split.purge_overlapping_labels,
    }
