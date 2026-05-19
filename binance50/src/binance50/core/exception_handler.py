import logging
from typing import Any

from binance50.audit.writer import audit_error
from binance50.core.error_classifier import error_to_safe_dict


def handle_exception(
    error: Exception, component: str, action: str, logger: logging.Logger | None = None
) -> dict[str, Any]:
    """
    Handle exception safely by logging, auditing, and returning a safe dictionary.
    """
    safe_dict = error_to_safe_dict(error)
    safe_dict["component"] = component  # Override component with the one where it was caught

    # Audit error
    audit_error(
        event_type="error_captured",
        component=component,
        action=action,
        error=error,
        metadata={"safe_dict": safe_dict},
    )

    # Log error
    if logger:
        # Avoid leaking secrets in the log message
        log_msg = f"[{component}] {action} failed: {safe_dict['message']} (Code: {safe_dict['error_code']})"
        if safe_dict.get("severity") == "critical":
            logger.critical(log_msg, exc_info=error)
        else:
            logger.error(log_msg, exc_info=error)

    return safe_dict


def log_exception_once(error: Exception, logger: logging.Logger) -> None:
    # Basic implementation, can be extended to use caching for collapse
    handle_exception(error, component="unknown", action="log_once", logger=logger)


def build_user_safe_error_report(error: Exception) -> dict[str, Any]:
    return error_to_safe_dict(error)


def should_collapse_repeated_error(error: Exception, window_seconds: int) -> bool:
    # Phase 3 simple stub
    return False
