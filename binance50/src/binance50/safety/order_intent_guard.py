from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionIntentError

from binance50.execution.models import ExecutionIntentDraft
from binance50.execution.validators import (
    validate_execution_intent_draft,
    validate_intent_not_order,
    validate_no_exchange_identifiers,
    validate_no_quantity_price_leverage,
)


def assert_intent_is_not_order(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    validate_intent_not_order(intent, config)


def assert_intent_mode_allowed(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    allowed = ["sandbox"]
    if intent.mode.value not in allowed:
        raise ExecutionIntentError(f"Intent mode {intent.mode} is not allowed. Only sandbox is allowed in Phase 28.")


def assert_no_quantity_price_leverage(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    validate_no_quantity_price_leverage(intent, config)


def assert_no_exchange_order_identifiers(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    validate_no_exchange_identifiers(intent, config)


def assert_intent_has_required_internal_metadata(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    validate_execution_intent_draft(intent, config)


def build_order_intent_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "sandbox_mode_only": True,
        "quantity_price_leverage_rejected": config.execution.intents.reject_quantity_output_by_default,
        "exchange_identifiers_rejected": config.execution.intents.reject_order_id_fields
    }
