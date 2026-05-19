import logging
from typing import Any

from binance50.audit.events import AuditEvent, AuditEventType
from binance50.logging.context import get_correlation_id, get_runtime_context


class AuditWriter:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("binance50.audit")

    def write_event(self, event: AuditEvent) -> None:
        """Write an audit event to the audit log."""
        try:
            # Inject context if missing
            ctx = get_runtime_context()
            if not event.correlation_id:
                event.correlation_id = get_correlation_id()
            if not event.environment_profile:
                event.environment_profile = ctx.get("environment_profile")
            if not event.trading_mode:
                event.trading_mode = ctx.get("trading_mode")
            if not event.market_scope:
                event.market_scope = ctx.get("market_scope")

            event_dict = event.to_dict()
            # The SafeJsonFormatter on the handler will dump this as JSON
            # Pass extra values but rename `message` to avoid collision with LogRecord.message
            extra = event_dict.copy()
            if "message" in extra:
                extra["audit_message"] = extra.pop("message")
            self.logger.info("AUDIT_EVENT", extra=extra)
        except Exception as e:
            # Fallback console log to avoid infinite loop
            print(f"CRITICAL: Failed to write audit event: {e}")

    def write_dict(self, payload: dict[str, Any]) -> None:
        event = AuditEvent(
            event_type=payload.get("event_type", "unknown"),
            component=payload.get("component", "unknown"),
            action=payload.get("action", "unknown"),
            status=payload.get("status", "success"),
            severity=payload.get("severity", "info"),
            message=payload.get("message", ""),
            metadata=payload.get("metadata", {}),
            error_code=payload.get("error_code"),
            exception_class=payload.get("exception_class"),
        )
        self.write_event(event)

    def flush(self) -> None:
        """Flush the underlying handlers."""
        for handler in self.logger.handlers:
            handler.flush()


_default_writer: AuditWriter | None = None


def get_audit_writer(config: Any = None) -> AuditWriter:
    global _default_writer
    if _default_writer is None:
        _default_writer = AuditWriter()
    return _default_writer


def audit_event(
    event_type: AuditEventType | str,
    component: str,
    action: str,
    status: str = "success",
    message: str = "",
    metadata: dict[str, Any] | None = None,
    severity: str = "info",
) -> None:
    """Helper to write a generic audit event."""
    writer = get_audit_writer()
    event = AuditEvent(
        event_type=event_type,
        component=component,
        action=action,
        status=status,
        message=message,
        metadata=metadata or {},
        severity=severity,
    )
    writer.write_event(event)


def audit_error(
    event_type: AuditEventType | str,
    component: str,
    action: str,
    error: Exception,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Helper to write an error audit event."""
    writer = get_audit_writer()
    from binance50.core.exceptions import Binance50Error

    error_code = None
    exception_class = error.__class__.__name__
    if isinstance(error, Binance50Error):
        error_code = error.error_code

    event = AuditEvent(
        event_type=event_type,
        component=component,
        action=action,
        status="failed",
        severity="error",
        message=str(error),
        metadata=metadata or {},
        error_code=error_code,
        exception_class=exception_class,
    )
    writer.write_event(event)
