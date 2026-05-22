from typing import Any

from binance50.core.exceptions import (
    Binance50Error,
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
    StreamBufferOverflowError,
    StreamConnectionDisabledError,
    StreamDuplicateEventError,
    StreamParseError,
    StreamRouteError,
    StreamStaleEventError,
)


def classify_http_status(
    status_code: int, payload: dict[str, Any] | None = None
) -> type[Binance50Error]:
    """Classify error based on HTTP status code."""
    if status_code == 429:
        return BinanceRateLimitError
    elif status_code == 418:
        return BinanceIpBanError
    elif status_code in (401,):
        return BinanceAuthenticationError
    elif status_code in (403,):
        return BinancePermissionError
    elif 500 <= status_code < 600:
        if status_code in (500, 502, 503, 504):
            # In trading context 5xx means unknown execution status
            return BinanceUnknownExecutionStatusError
        return BinanceServerError
    return BinanceApiError


def classify_binance_error(
    code: int | None, msg: str | None, status_code: int | None = None
) -> type[Binance50Error]:
    """Classify specific binance API error codes and messages."""
    msg_lower = (msg or "").lower()

    if code == -1021 or "timestamp" in msg_lower or "recvwindow" in msg_lower:
        return BinanceTimestampError

    if code == -2010 and "insufficient balance" in msg_lower:
        return BinanceInsufficientBalanceError

    if "min_notional" in msg_lower or "lot_size" in msg_lower or "filter" in msg_lower:
        return BinanceSymbolFilterError

    if status_code is not None:
        return classify_http_status(status_code)

    return BinanceApiError


def is_retryable_error(error: Exception) -> bool:
    """Check if the error is retryable."""
    if isinstance(error, Binance50Error):
        return error.retryable
    return False


def error_to_safe_dict(error: Exception) -> dict[str, Any]:
    """Convert an exception to a safe dictionary representation."""
    from binance50.logging.redaction import redact_text

    if isinstance(error, Binance50Error):
        return error.to_dict(redacted=True)

    return {
        "error_code": "UNHANDLED_EXCEPTION",
        "message": redact_text(str(error)),
        "component": "unknown",
        "severity": "error",
        "retryable": False,
        "user_action_required": False,
        "metadata": {},
        "exception_class": error.__class__.__name__,
    }


def classify_stream_error(msg: str) -> type[Binance50Error]:
    msg_lower = msg.lower()
    if "missing" in msg_lower or "invalid numeric" in msg_lower:
        return StreamParseError
    if "stale" in msg_lower:
        return StreamStaleEventError
    if "duplicate" in msg_lower:
        return StreamDuplicateEventError
    if "overflow" in msg_lower or "buffer full" in msg_lower:
        return StreamBufferOverflowError
    if "route" in msg_lower or "unsupported" in msg_lower:
        return StreamRouteError
    if "real connect disabled" in msg_lower or "disabled in phase 9" in msg_lower:
        return StreamConnectionDisabledError
    from binance50.core.exceptions import StreamError
    return StreamError
