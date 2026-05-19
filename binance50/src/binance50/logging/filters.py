import logging

from binance50.logging.context import get_correlation_id, get_runtime_context
from binance50.logging.redaction import redact_mapping, redact_sequence, redact_text


class RedactionFilter(logging.Filter):
    """Filters out sensitive information from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Redact message
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg)

        # Redact args
        if isinstance(record.args, tuple):
            record.args = tuple(redact_sequence(list(record.args)))
        elif isinstance(record.args, dict):
            record.args = redact_mapping(record.args)

        # Redact extra
        # 'extra' dictionary attributes are dynamically added to the record
        # but we need to intercept them before formatter processes them if they are in __dict__
        # A simpler way is to let formatters handle extra redaction or do it here on known dicts.

        return True


class CorrelationIdFilter(logging.Filter):
    """Adds a correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


class RuntimeContextFilter(logging.Filter):
    """Adds runtime context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = get_runtime_context()
        record.environment_profile = ctx.get("environment_profile", "unknown")
        record.trading_mode = ctx.get("trading_mode", "unknown")
        record.market_scope = ctx.get("market_scope", "unknown")
        record.app_version = ctx.get("app_version", "unknown")
        return True
