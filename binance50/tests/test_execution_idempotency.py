import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionIdempotencyError
from binance50.execution.idempotency import build_correlation_id, build_idempotency_key, validate_idempotency_key

def test_build_correlation_id():
    config = get_config()
    cid = build_correlation_id("run1", "cand1", config)
    assert cid == "corr_run1_cand1"

def test_build_idempotency_key():
    config = get_config()
    k1 = build_idempotency_key("run1", "cand1", "BTCUSDT", "buy", "sandbox", "1000", config)
    k2 = build_idempotency_key("run1", "cand1", "BTCUSDT", "buy", "sandbox", "1000", config)
    assert k1 == k2
    assert k1.startswith("idk_")

def test_validate_idempotency_key():
    config = get_config()
    validate_idempotency_key("idk_123", config)
    with pytest.raises(ExecutionIdempotencyError):
        validate_idempotency_key("invalid", config)
