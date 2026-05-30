import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionIntentError, ExchangeOrderIdentifierDetectedError
from binance50.execution.validators import (
    validate_execution_intent_draft,
    validate_no_quantity_price_leverage,
    validate_no_exchange_identifiers
)
from binance50.execution.models import ExecutionIntentDraft, ExecutionMode, ExecutionIntentKind, ExecutionSide, ExecutionSourceType, ExecutionIntentStatus
from datetime import datetime, timezone

def test_validate_intent_draft_missing_fields():
    config = get_config()
    intent = ExecutionIntentDraft(
        intent_id="1", mode=ExecutionMode.sandbox, kind=ExecutionIntentKind.hypothetical_review,
        status=ExecutionIntentStatus.draft_created, source_type=ExecutionSourceType.manual_review,
        source_run_id="1", source_candidate_id="1", symbol="", market_scope="spot", interval="1m",
        side=ExecutionSide.buy, hypothetical_notional_usdt=None, quantity=None, price=None,
        order_type=None, time_in_force=None, correlation_id="1", idempotency_key="1",
        source_trace="1", safety_scan_id=None, explanation="1", metadata={}, created_at_utc=datetime.now(timezone.utc)
    )
    with pytest.raises(ExecutionIntentError, match="Symbol is missing"):
        validate_execution_intent_draft(intent, config)

def test_validate_no_quantity_price():
    config = get_config()
    intent = ExecutionIntentDraft(
        intent_id="1", mode=ExecutionMode.sandbox, kind=ExecutionIntentKind.hypothetical_review,
        status=ExecutionIntentStatus.draft_created, source_type=ExecutionSourceType.manual_review,
        source_run_id="1", source_candidate_id="1", symbol="BTCUSDT", market_scope="spot", interval="1m",
        side=ExecutionSide.buy, hypothetical_notional_usdt=None, quantity=1.0, price=None,
        order_type=None, time_in_force=None, correlation_id="1", idempotency_key="1",
        source_trace="1", safety_scan_id=None, explanation="1", metadata={}, created_at_utc=datetime.now(timezone.utc)
    )
    with pytest.raises(ExecutionIntentError, match="Quantity is set"):
        validate_no_quantity_price_leverage(intent, config)
