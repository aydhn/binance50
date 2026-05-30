import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionPayloadSafetyError
from binance50.execution.payloads import (
    detect_api_credentials,
    detect_signed_payload,
    detect_order_identifiers,
    scan_payload_for_forbidden_fields,
    assert_payload_safe
)

def test_detect_api_credentials():
    assert detect_api_credentials({"api_key": "mysecret"})
    assert detect_api_credentials({"listenKey": "somelistenkey"})

def test_detect_signed_payload():
    assert detect_signed_payload({"signature": "123", "timestamp": 1234567890})

def test_detect_order_identifiers():
    assert detect_order_identifiers({"clientOrderId": "some_id"})

def test_scan_payload():
    config = get_config()
    scan = scan_payload_for_forbidden_fields({"api_key": "x"}, "test_intent", config)
    assert not scan.passed
    assert scan.blocked
    assert scan.credential_detected

def test_assert_payload_safe_raises():
    config = get_config()
    with pytest.raises(ExecutionPayloadSafetyError):
        assert_payload_safe({"orderId": 123}, config)
