from pathlib import Path

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    DestructiveActionBlockedError,
    UnsafeConfigurationError,
)
from binance50.storage.schemas import DatasetSchema


def assert_storage_config_safe(config: AppConfig) -> None:
    if not config.storage.enabled:
        return

    if config.storage.safety.allow_delete:
        # Consider emitting a warning log in real system
        pass

    if config.storage.safety.allow_destructive_migration:
        raise DestructiveActionBlockedError(
            "allow_destructive_migration=True is blocked in Phase 10"
        )

    if not config.storage.datasets.allowed_dataset_names:
        raise UnsafeConfigurationError("allowed_dataset_names cannot be empty")


def assert_dataset_name_allowed(dataset_name: str, config: AppConfig) -> None:
    if config.storage.safety.block_unknown_dataset_names:
        if dataset_name not in config.storage.datasets.allowed_dataset_names:
            raise UnsafeConfigurationError(f"Dataset {dataset_name} is blocked")


def assert_no_secret_columns(df: pd.DataFrame) -> None:
    secret_words = ["api_key", "secret", "token", "signature", "password"]
    for col in df.columns:
        col_lower = col.lower()
        if any(secret in col_lower for secret in secret_words):
            raise UnsafeConfigurationError(f"Secret-like column name detected: {col}")


def assert_safe_storage_path(path: Path, config: AppConfig) -> None:
    from binance50.storage.paths import assert_path_inside_storage

    assert_path_inside_storage(path, config)


def assert_destructive_action_allowed(config: AppConfig, action: str) -> None:
    if not config.storage.safety.allow_delete:
        raise DestructiveActionBlockedError(f"Action '{action}' is blocked by allow_delete=False")


def assert_schema_safe(schema: DatasetSchema) -> None:
    secret_words = ["api_key", "secret", "token", "signature", "password"]
    for col in schema.columns:
        col_lower = col.name.lower()
        if any(secret in col_lower for secret in secret_words):
            raise UnsafeConfigurationError(f"Secret-like column in schema detected: {col.name}")


def build_storage_safety_report(config: AppConfig) -> dict:
    return {
        "status": "safe",
        "allow_delete": config.storage.safety.allow_delete,
        "allow_destructive_migration": config.storage.safety.allow_destructive_migration,
        "block_paths_outside_project": config.storage.safety.block_paths_outside_project,
        "block_secret_columns": config.storage.safety.block_secret_columns,
    }
