import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionIntentError
from binance50.safety.order_intent_guard import assert_intent_mode_allowed
from binance50.execution.models import ExecutionIntentDraft, ExecutionMode, ExecutionIntentKind, ExecutionSide, ExecutionSourceType, ExecutionIntentStatus
from datetime import datetime, timezone

def test_order_intent_mode_allowed():
    config = get_config()
    intent = ExecutionIntentDraft(
        intent_id="1", mode=ExecutionMode.live_candidate, kind=ExecutionIntentKind.hypothetical_review,
        status=ExecutionIntentStatus.draft_created, source_type=ExecutionSourceType.manual_review,
        source_run_id="1", source_candidate_id="1", symbol="BTCUSDT", market_scope="spot", interval="1m",
        side=ExecutionSide.buy, hypothetical_notional_usdt=None, quantity=None, price=None,
        order_type=None, time_in_force=None, correlation_id="1", idempotency_key="1",
        source_trace="1", safety_scan_id=None, explanation="1", metadata={}, created_at_utc=datetime.now(timezone.utc)
    )
    with pytest.raises(ExecutionIntentError, match="not allowed"):
        assert_intent_mode_allowed(intent, config)
