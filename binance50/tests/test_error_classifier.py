from binance50.core.error_classifier import (
    classify_binance_error,
    classify_http_status,
    error_to_safe_dict,
    is_retryable_error,
)
from binance50.core.exceptions import (
    BinanceApiError,
    BinanceAuthenticationError,
    BinanceInsufficientBalanceError,
    BinanceIpBanError,
    BinancePermissionError,
    BinanceRateLimitError,
    BinanceServerError,
    BinanceSymbolFilterError,
    BinanceTimestampError,
    BinanceUnknownExecutionStatusError,
)


def test_classify_http_status():
    assert classify_http_status(429) == BinanceRateLimitError
    assert classify_http_status(418) == BinanceIpBanError
    assert classify_http_status(401) == BinanceAuthenticationError
    assert classify_http_status(403) == BinancePermissionError
    assert classify_http_status(500) == BinanceUnknownExecutionStatusError
    assert classify_http_status(502) == BinanceUnknownExecutionStatusError
    assert classify_http_status(501) == BinanceServerError
    assert classify_http_status(400) == BinanceApiError


def test_classify_binance_error():
    assert classify_binance_error(-1021, "Timestamp for this request...") == BinanceTimestampError
    assert (
        classify_binance_error(-2010, "Account has insufficient balance for requested action.")
        == BinanceInsufficientBalanceError
    )
    assert classify_binance_error(-1013, "Filter failure: MIN_NOTIONAL") == BinanceSymbolFilterError
    assert classify_binance_error(-1013, "Filter failure: LOT_SIZE") == BinanceSymbolFilterError

    # Fallbacks
    assert classify_binance_error(-1000, "Unknown error", status_code=429) == BinanceRateLimitError
    assert classify_binance_error(-1000, "Unknown error") == BinanceApiError


def test_is_retryable_error():
    assert is_retryable_error(BinanceRateLimitError("test")) is True
    assert is_retryable_error(BinanceTimestampError("test")) is True
    assert is_retryable_error(BinanceIpBanError("test")) is False
    assert is_retryable_error(ValueError("test")) is False


def test_error_to_safe_dict():
    # Test with Binance50Error
    err = BinanceRateLimitError("test", metadata={"api_key": "1234567890"})
    d = error_to_safe_dict(err)
    assert d["error_code"] == "BINANCE_RATE_LIMIT"
    assert "***REDACTED***" in d["metadata"]["api_key"]

    # Test with standard Exception
    err2 = ValueError("Bad value token=1234567890")
    d2 = error_to_safe_dict(err2)
    assert d2["error_code"] == "UNHANDLED_EXCEPTION"
    assert "***REDACTED***" in d2["message"]
    assert "1234567890" not in d2["message"]
    assert d2["exception_class"] == "ValueError"
