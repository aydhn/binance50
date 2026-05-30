from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    CredentialDetectedError,
    ExchangeOrderIdentifierDetectedError,
    ExecutionIntentError,
    ExecutionPayloadSafetyError,
)

from .models import ExecutionDryRunResult, ExecutionIntentDraft, ExecutionSafetyRunResult
from .payloads import assert_payload_safe, detect_api_credentials, detect_order_identifiers


def validate_execution_intent_draft(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if config.execution.intents.reject_missing_symbol and not intent.symbol:
        raise ExecutionIntentError("Symbol is missing in intent draft.")
    if config.execution.intents.reject_missing_side and not intent.side:
        raise ExecutionIntentError("Side is missing in intent draft.")
    if config.execution.intents.require_correlation_id and not intent.correlation_id:
        raise ExecutionIntentError("Correlation ID is missing.")
    if config.execution.intents.require_idempotency_key and not intent.idempotency_key:
        raise ExecutionIntentError("Idempotency key is missing.")


def validate_intent_not_order(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if config.execution.intents.intent_draft_is_not_order:
        if intent.kind != "hypothetical_review" and intent.kind != "paper_candidate":
             # We might allow paper_candidate for later phases, but draft_is_not_order implies it's never a real order.
             if getattr(intent, 'mode', None) in ["live_candidate", "testnet_candidate"]:
                 raise ExecutionIntentError(f"Intent mode {intent.mode} indicates production order intent.")


def validate_no_quantity_price_leverage(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if config.execution.intents.reject_quantity_output_by_default and intent.quantity is not None:
        raise ExecutionIntentError("Quantity is set but should be None in Phase 28.")
    if config.execution.intents.reject_price_output_by_default and intent.price is not None:
        raise ExecutionIntentError("Price is set but should be None in Phase 28.")
    if config.execution.intents.reject_leverage_output and "leverage" in intent.metadata:
        raise ExecutionIntentError("Leverage is set in metadata.")


def validate_no_exchange_identifiers(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if config.execution.intents.reject_order_id_fields:
        identifiers = detect_order_identifiers(intent.metadata)
        if identifiers:
            raise ExchangeOrderIdentifierDetectedError(f"Exchange identifier detected: {identifiers}")


def validate_no_credentials(payload: dict[str, Any], config: AppConfig) -> None:
    creds = detect_api_credentials(payload)
    if creds:
        raise CredentialDetectedError(f"Credentials detected: {creds}")


def validate_dry_run_result(result: ExecutionDryRunResult, config: AppConfig) -> None:
    if not result.passed:
        raise ExecutionPayloadSafetyError(f"Dry run validation failed: {result.warnings}")


def validate_execution_safety_run_result(result: ExecutionSafetyRunResult, config: AppConfig) -> None:
    if not result.success:
        raise ExecutionPayloadSafetyError(f"Execution safety run failed: {result.error}")
