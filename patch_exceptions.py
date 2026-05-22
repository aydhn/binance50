with open("binance50/src/binance50/core/exceptions.py", "r") as f:
    content = f.read()

new_exceptions = """
# Phase 9 Stream Exceptions
class StreamError(Binance50Error):
    pass

class StreamConfigError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_CONFIG_INVALID)
        super().__init__(message, **kwargs)

class StreamConnectionDisabledError(StreamError):
    def __init__(self, message: str = "Real WebSocket connections are disabled in Phase 9", **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_REAL_CONNECT_DISABLED)
        super().__init__(message, **kwargs)

class StreamSubscriptionError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_SUBSCRIPTION_INVALID)
        super().__init__(message, **kwargs)

class StreamParseError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_PARSE_FAILED)
        super().__init__(message, **kwargs)

class StreamValidationError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_VALIDATION_FAILED)
        super().__init__(message, **kwargs)

class StreamBufferOverflowError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_BUFFER_OVERFLOW)
        super().__init__(message, **kwargs)

class StreamDuplicateEventError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_DUPLICATE_EVENT)
        super().__init__(message, **kwargs)

class StreamStaleEventError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_STALE_EVENT)
        super().__init__(message, **kwargs)

class StreamOutOfOrderError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_OUT_OF_ORDER)
        super().__init__(message, **kwargs)

class StreamReplayError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_REPLAY_FAILED)
        super().__init__(message, **kwargs)

class StreamRouteError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_ROUTE_INVALID)
        super().__init__(message, **kwargs)

class StreamLifecycleError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_LIFECYCLE_INVALID)
        super().__init__(message, **kwargs)

class RealtimeStoreError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.REALTIME_STORE_FAILED)
        super().__init__(message, **kwargs)
"""

if "StreamError" not in content:
    with open("binance50/src/binance50/core/exceptions.py", "w") as f:
        f.write(content.rstrip() + "\n" + new_exceptions)
