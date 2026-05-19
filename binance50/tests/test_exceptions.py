from binance50.core.exceptions import (
    Binance50Error,
    BinanceIpBanError,
    BinanceRateLimitError,
    BinanceUnknownExecutionStatusError,
)


def test_binance50_error_to_dict():
    err = Binance50Error(
        message="Test error",
        error_code="TEST_ERR",
        component="test_comp",
        severity="warning",
        retryable=True,
        metadata={"secret": "1234567890"},
    )

    d = err.to_dict()
    assert d["error_code"] == "TEST_ERR"
    assert d["message"] == "Test error"
    assert d["component"] == "test_comp"
    assert d["severity"] == "warning"
    assert d["retryable"] is True
    assert d["metadata"]["secret"] == "12***REDACTED***90"
    assert d["exception_class"] == "Binance50Error"


def test_binance50_error_with_context():
    err = Binance50Error("Test").with_context(new_field="value", api_key="1234567890")
    d = err.to_dict()
    assert d["metadata"]["new_field"] == "value"
    assert d["metadata"]["api_key"] == "12***REDACTED***90"


def test_safe_message():
    err = Binance50Error("Failed due to api_key=1234567890")
    assert "api_key=***REDACTED***" in err.safe_message()


def test_binance_rate_limit_error():
    err = BinanceRateLimitError("Rate limit exceeded")
    assert err.error_code == "BINANCE_RATE_LIMIT"
    assert err.retryable is True
    assert err.severity == "error"


def test_binance_ip_ban_error():
    err = BinanceIpBanError("IP banned")
    assert err.error_code == "BINANCE_IP_BAN"
    assert err.severity == "critical"
    assert err.user_action_required is True


def test_binance_unknown_execution_error():
    err = BinanceUnknownExecutionStatusError("500 Server Error")
    assert err.error_code == "BINANCE_UNKNOWN_EXECUTION_STATUS"
    assert err.severity == "critical"
    assert err.user_action_required is True
