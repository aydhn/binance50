from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskValidationError
from binance50.risk.models import RiskAssessment, RiskRunResult

_EXECUTION_FIELD_BLACKLIST = [
    "order_id",
    "quantity",
    "qty",
    "leverage_to_set",
    "leverage",
    "margin",
    "entry_price",
    "exit_price",
    "stop_loss",
    "take_profit",
    "liquidation_price",
    "order_type",
    "side",
    "reduce_only",
    "position_side",
    "base_qty",
    "quote_qty",
]


def validate_no_execution_fields(payload: Any) -> None:
    if isinstance(payload, dict):
        for k, v in payload.items():
            if k in _EXECUTION_FIELD_BLACKLIST:
                raise RiskValidationError(f"Forbidden execution field detected: {k}")
            validate_no_execution_fields(v)
    elif isinstance(payload, list):
        for item in payload:
            validate_no_execution_fields(item)
    elif hasattr(payload, "model_dump"):
        validate_no_execution_fields(payload.model_dump())


def validate_no_order_language(text: str) -> None:
    order_words = ["buy", "sell", "order", "execute", "long", "short", "position"]
    text_lower = text.lower()
    for w in order_words:
        if w in text_lower:
            raise RiskValidationError(f"Order-like language detected: {w}")


def validate_no_future_target_label_columns(df: pd.DataFrame) -> None:
    for col in df.columns:
        if "future" in col.lower() or "target" in col.lower() or "label" in col.lower():
            raise RiskValidationError(f"Future/target/label column detected: {col}")


def validate_risk_input_signals(scored_signals: list[Any], config: AppConfig) -> None:
    for sig in scored_signals:
        validate_no_execution_fields(sig)


def validate_risk_regime_context(regimes: list[Any] | None, config: AppConfig) -> None:
    if regimes:
        for r in regimes:
            validate_no_execution_fields(r)


def validate_risk_assessment(assessment: RiskAssessment, config: AppConfig) -> None:
    validate_no_execution_fields(assessment)
    if config.risk.quality.reject_order_like_language:
        validate_no_order_language(assessment.explanation)


def validate_risk_result(result: RiskRunResult, config: AppConfig) -> None:
    validate_no_execution_fields(result)
    for a in result.assessments:
        validate_risk_assessment(a, config)
    for a in result.rejected_assessments:
        validate_risk_assessment(a, config)
