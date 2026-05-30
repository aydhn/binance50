import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionCircuitBreakerError
from binance50.execution.circuit_breaker import check_max_intents_per_run
from binance50.execution.models import ExecutionIntentDraft, ExecutionMode, ExecutionIntentKind, ExecutionSide, ExecutionSourceType, ExecutionIntentStatus
from datetime import datetime, timezone

def test_circuit_breaker_max_run():
    config = get_config()
    config.execution.circuit_breaker.max_intents_per_run = 1
    intent = ExecutionIntentDraft(
        intent_id="1", mode=ExecutionMode.sandbox, kind=ExecutionIntentKind.hypothetical_review,
        status=ExecutionIntentStatus.draft_created, source_type=ExecutionSourceType.manual_review,
        source_run_id="1", source_candidate_id="1", symbol="BTCUSDT", market_scope="spot", interval="1m",
        side=ExecutionSide.buy, hypothetical_notional_usdt=None, quantity=None, price=None,
        order_type=None, time_in_force=None, correlation_id="1", idempotency_key="1",
        source_trace="1", safety_scan_id=None, explanation="1", metadata={}, created_at_utc=datetime.now(timezone.utc)
    )
    with pytest.raises(ExecutionCircuitBreakerError, match="Max intents"):
        check_max_intents_per_run([intent, intent], config)
