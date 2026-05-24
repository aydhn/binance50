import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeLeakageError, RegimeValidationError
from binance50.regimes.models import RegimeClassification, RegimeRunResult


def validate_no_future_target_label_columns(df: pd.DataFrame) -> None:
    invalid_cols = ["target", "label", "future_return", "next_close", "forward_return"]
    for col in invalid_cols:
        if col in df.columns:
            raise RegimeLeakageError(f"Leakage detected: column {col} found.")


def validate_no_execution_columns(df: pd.DataFrame) -> None:
    invalid_cols = [
        "order_id",
        "quantity",
        "leverage",
        "entry_price",
        "exit_price",
        "stop_loss",
        "take_profit",
        "position_size",
    ]
    for col in invalid_cols:
        if col in df.columns:
            raise RegimeLeakageError(f"Execution column blocked: {col}")


def validate_closed_candles_only(df: pd.DataFrame, config: AppConfig) -> None:
    if config.regimes.require_closed_candles and "is_closed" in df.columns:
        if not df["is_closed"].all():
            raise RegimeLeakageError("Unclosed candles found in input data")


def validate_regime_input_dataframe(df: pd.DataFrame, config: AppConfig) -> None:
    if len(df) < config.regimes.classifier.min_rows_required:
        raise RegimeValidationError(
            f"Input dataframe requires at least {config.regimes.classifier.min_rows_required} rows"
        )
    validate_no_future_target_label_columns(df)
    validate_no_execution_columns(df)
    validate_closed_candles_only(df, config)


def validate_regime_feature_dataframe(df: pd.DataFrame, config: AppConfig) -> None:
    validate_no_future_target_label_columns(df)
    validate_no_execution_columns(df)


def validate_regime_classification(classification: RegimeClassification, config: AppConfig) -> None:
    if (
        not config.regimes.thresholds.min_regime_confidence
        <= classification.confidence
        <= config.regimes.thresholds.max_regime_confidence
    ):
        raise RegimeValidationError(f"Confidence {classification.confidence} out of range")

    if config.regimes.quality.reject_missing_explanation and not classification.explanation:
        raise RegimeValidationError("Missing explanation for classification")


def validate_regime_result(result: RegimeRunResult, config: AppConfig) -> None:
    for c in result.classifications:
        validate_regime_classification(c, config)
