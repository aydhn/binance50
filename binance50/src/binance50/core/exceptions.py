from typing import Any, Self

from binance50.core import error_codes


class Binance50Error(Exception):
    """Base exception for binance50."""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        component: str = "core",
        severity: str = "error",
        retryable: bool = False,
        user_action_required: bool = False,
        metadata: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.component = component
        self.severity = severity
        self.retryable = retryable
        self.user_action_required = user_action_required
        self.metadata = metadata or {}
        self.cause = cause
        if cause:
            self.__cause__ = cause

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        """Convert exception to dictionary representation."""
        # Note: True redaction logic will be applied in the exception handler or logging layer
        # if `redacted` is True. For now we return the metadata.
        from binance50.logging.redaction import redact_mapping

        md = redact_mapping(self.metadata) if redacted else self.metadata
        return {
            "error_code": self.error_code,
            "message": self.message,
            "component": self.component,
            "severity": self.severity,
            "retryable": self.retryable,
            "user_action_required": self.user_action_required,
            "metadata": md,
            "exception_class": self.__class__.__name__,
        }

    def safe_message(self) -> str:
        """Return a message safe for public logging/display."""
        from binance50.logging.redaction import redact_text

        return redact_text(self.message)

    def with_context(self, **metadata: Any) -> Self:
        """Add metadata to the exception context."""
        self.metadata.update(metadata)
        return self


# General Classes
class ConfigError(Binance50Error):
    """Configuration related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.CONFIG_LOAD_FAILED)
        kwargs.setdefault("component", "config")
        super().__init__(message, **kwargs)


class ConfigValidationError(ConfigError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.CONFIG_VALIDATION_FAILED)
        super().__init__(message, **kwargs)


class EnvironmentProfileError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.ENVIRONMENT_PROFILE_INVALID)
        kwargs.setdefault("component", "environment")
        super().__init__(message, **kwargs)


class SafetyError(Binance50Error):
    """Safety and guard related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SAFETY_CHECK_FAILED)
        kwargs.setdefault("component", "safety")
        kwargs.setdefault("severity", "critical")
        super().__init__(message, **kwargs)


class SecretLeakError(SafetyError):
    """Secret leak related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SECRET_LEAK_DETECTED)
        super().__init__(message, **kwargs)


class LiveTradingBlockedError(SafetyError):
    """Live trading is blocked."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.LIVE_TRADING_BLOCKED)
        super().__init__(message, **kwargs)


class InvalidTradingModeError(SafetyError):
    """Invalid trading mode."""

    pass


class LoggingSetupError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.LOGGING_SETUP_FAILED)
        kwargs.setdefault("component", "logging")
        super().__init__(message, **kwargs)


class AuditWriteError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.AUDIT_WRITE_FAILED)
        kwargs.setdefault("component", "audit")
        super().__init__(message, **kwargs)


class DataValidationError(Binance50Error):
    pass


class DependencyMissingError(Binance50Error):
    pass


class UnsupportedFeatureError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.UNSUPPORTED_FEATURE)
        super().__init__(message, **kwargs)


class StateError(Binance50Error):
    pass


class RuntimeInvariantError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.RUNTIME_INVARIANT_FAILED)
        super().__init__(message, **kwargs)


# Binance-specific Classes
class BinanceApiError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("component", "binance_api")
        super().__init__(message, **kwargs)


class BinanceRateLimitError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_RATE_LIMIT)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class BinanceIpBanError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_IP_BAN)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinanceRequestError(BinanceApiError):
    pass


class BinanceServerError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_SERVER_ERROR)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class BinanceUnknownExecutionStatusError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_UNKNOWN_EXECUTION_STATUS)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinanceAuthenticationError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_AUTH_FAILED)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinancePermissionError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_PERMISSION_DENIED)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinanceTimestampError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_TIMESTAMP_ERROR)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class BinanceInsufficientBalanceError(BinanceApiError):
    pass


class BinanceOrderRejectedError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_ORDER_REJECTED)
        super().__init__(message, **kwargs)


class BinanceSymbolFilterError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_SYMBOL_FILTER_FAILED)
        super().__init__(message, **kwargs)


class BinanceWebSocketError(BinanceApiError):
    pass


class BinanceUserDataStreamError(BinanceApiError):
    pass
