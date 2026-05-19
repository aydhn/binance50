import json
import logging
from datetime import UTC, datetime


class SafeJsonFormatter(logging.Formatter):
    """Formatter that outputs logs in a safe JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        # Format exception traceback if present
        exc_info = None
        if record.exc_info:
            exc_info = self.formatException(record.exc_info)

        log_dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": getattr(record, "audit_message", record.getMessage()),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
            "correlation_id": getattr(record, "correlation_id", None),
            "environment_profile": getattr(record, "environment_profile", "unknown"),
            "trading_mode": getattr(record, "trading_mode", "unknown"),
            "market_scope": getattr(record, "market_scope", "unknown"),
        }

        # Include custom extra fields like 'metadata', 'event_type', etc.
        for key, value in record.__dict__.items():
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "message",
                "module",
                "msecs",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "taskName",
                "correlation_id",
                "environment_profile",
                "trading_mode",
                "market_scope",
                "audit_message",
            ]:
                log_dict[key] = value

        if exc_info:
            log_dict["traceback"] = exc_info
            if hasattr(record, "exc_text") and record.exc_text:
                # exc_text might contain secrets, redact it before assigning
                from binance50.logging.redaction import redact_text

                log_dict["traceback"] = redact_text(record.exc_text)

        # Redact the entire dictionary just to be safe
        from binance50.logging.redaction import redact_mapping

        safe_dict = redact_mapping(log_dict)

        return json.dumps(safe_dict)


class SafeConsoleFormatter(logging.Formatter):
    """Formatter that outputs safe human-readable logs for the console."""

    def __init__(
        self,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
    ):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        # The RedactionFilter should have already processed the message,
        # but we can do a final safety check if we want.
        # For now, rely on RedactionFilter.
        return super().format(record)
