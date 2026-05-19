import functools
from collections.abc import Callable
from typing import Any

from binance50.audit.events import AuditEventType
from binance50.audit.writer import audit_error, audit_event


def audited_action(event_type: AuditEventType | str, component: str, action: str) -> Callable[..., Any]:
    """
    Decorator to automatically audit the start, success, and failure of a function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Note: We don't log args/kwargs by default to avoid accidental secret leaks
            # We assume the function handles its own specific metadata auditing if needed
            try:
                result = func(*args, **kwargs)
                audit_event(
                    event_type=event_type,
                    component=component,
                    action=action,
                    status="success",
                    message=f"Action '{action}' completed successfully.",
                )
                return result
            except Exception as e:
                audit_error(
                    event_type="error_captured",
                    component=component,
                    action=action,
                    error=e,
                    metadata={"original_event_type": getattr(event_type, "value", event_type)},
                )
                raise

        return wrapper

    return decorator
