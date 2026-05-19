import contextvars
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)
_runtime_context: contextvars.ContextVar[dict[str, str]] = contextvars.ContextVar(
    "runtime_context", default={}
)


def get_correlation_id() -> str:
    """Get the current correlation ID, generating one if not set."""
    cid = _correlation_id.get()
    if not cid:
        cid = str(uuid.uuid4())
        _correlation_id.set(cid)
    return cid


def set_correlation_id(correlation_id: str | None = None) -> str:
    """Set the correlation ID."""
    cid = correlation_id or str(uuid.uuid4())
    _correlation_id.set(cid)
    return cid


def reset_correlation_id(token: contextvars.Token[Any]) -> None:
    """Reset the correlation ID context."""
    _correlation_id.reset(token)


@contextmanager
def correlation_context(correlation_id: str | None = None) -> Generator[str, None, None]:
    """Context manager for managing correlation IDs."""
    cid = correlation_id or str(uuid.uuid4())
    token = _correlation_id.set(cid)
    try:
        yield cid
    finally:
        _correlation_id.reset(token)


def get_runtime_context() -> dict[str, str]:
    """Get the current runtime context."""
    return _runtime_context.get().copy()


def set_runtime_context(
    environment_profile: str, trading_mode: str, market_scope: str, app_version: str | None = None
) -> None:
    """Set the runtime context."""
    ctx = {
        "environment_profile": environment_profile,
        "trading_mode": trading_mode,
        "market_scope": market_scope,
    }
    if app_version:
        ctx["app_version"] = app_version
    _runtime_context.set(ctx)


def clear_runtime_context() -> None:
    """Clear the runtime context."""
    _runtime_context.set({})
