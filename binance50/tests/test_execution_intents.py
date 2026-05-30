import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionModeError
from binance50.execution.intents import ExecutionIntentBuilder

def test_build_sandbox_intent_draft():
    config = get_config()
    source = {
        "symbol": "ETHUSDT",
        "side": "buy",
        "hypothetical_notional_usdt": 500.0,
        "source_run_id": "run1",
        "source_candidate_id": "cand1"
    }

    intent = ExecutionIntentBuilder.build_sandbox_intent_draft(source, config)
    assert intent.symbol == "ETHUSDT"
    assert intent.side == "buy"
    assert intent.quantity is None
    assert intent.price is None
    assert intent.hypothetical_notional_usdt == 500.0

def test_build_sandbox_intent_draft_fails_if_mode_disabled():
    config = get_config()
    config.execution.allowed_modes.sandbox.enabled = False
    source = {"symbol": "ETHUSDT", "side": "buy"}
    with pytest.raises(ExecutionModeError):
        ExecutionIntentBuilder.build_sandbox_intent_draft(source, config)
