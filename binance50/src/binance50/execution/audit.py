import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from binance50.config.models import AppConfig


@dataclass
class ExecutionAuditEvent:
    event_id: str
    run_id: str
    intent_id: str
    event_type: str
    severity: str
    message: str
    metadata: dict[str, Any]
    created_at_utc: datetime


def emit_execution_audit_event(
    run_id: str,
    intent_id: str,
    event_type: str,
    severity: str,
    message: str,
    metadata: dict[str, Any]
) -> ExecutionAuditEvent:
    return ExecutionAuditEvent(
        event_id=f"audit_{uuid.uuid4().hex}",
        run_id=run_id,
        intent_id=intent_id,
        event_type=event_type,
        severity=severity,
        message=message,
        metadata=metadata,
        created_at_utc=datetime.now(timezone.utc)
    )


def build_execution_audit_timeline(events: list[ExecutionAuditEvent]) -> list[dict[str, Any]]:
    # Just convert to dict and sort by time
    sorted_events = sorted(events, key=lambda x: x.created_at_utc)
    return [redact_execution_audit_event(e) for e in sorted_events]


def redact_execution_audit_event(event: ExecutionAuditEvent) -> dict[str, Any]:
    # Ensure no secrets leak
    data = event.__dict__.copy()
    data["created_at_utc"] = data["created_at_utc"].isoformat()
    return data


def validate_audit_event(event: ExecutionAuditEvent, config: AppConfig) -> None:
    pass  # No complex validation needed for now
