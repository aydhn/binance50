from datetime import datetime, timezone

from binance50.execution.models import (
    ExecutionIntentDraft,
    ExecutionIntentKind,
    ExecutionIntentStatus,
    ExecutionMode,
    ExecutionSide,
    ExecutionSourceType,
)

def test_execution_models_instantiation():
    intent = ExecutionIntentDraft(
        intent_id="intent_123",
        mode=ExecutionMode.sandbox,
        kind=ExecutionIntentKind.hypothetical_review,
        status=ExecutionIntentStatus.draft_created,
        source_type=ExecutionSourceType.portfolio_construction_sandbox,
        source_run_id="run_123",
        source_candidate_id="cand_123",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        side=ExecutionSide.buy,
        hypothetical_notional_usdt=None,
        quantity=None,
        price=None,
        order_type=None,
        time_in_force=None,
        correlation_id="corr_123",
        idempotency_key="idk_123",
        source_trace="trace_info",
        safety_scan_id=None,
        explanation="test intent",
        metadata={},
        created_at_utc=datetime.now(timezone.utc)
    )
    assert intent.intent_id == "intent_123"
    assert intent.mode == ExecutionMode.sandbox
    assert intent.quantity is None
