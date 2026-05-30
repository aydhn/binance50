import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any
from binance50.config.models import AppConfig

class PaperAuditEvent(BaseModel):
    audit_event_id: str
    run_id: str
    paper_order_id: str | None
    event_type: str
    severity: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def emit_paper_audit_event(run_id: str, event_type: str, severity: str, message: str, order_id: str = None) -> PaperAuditEvent:
    return PaperAuditEvent(
        audit_event_id=f"audit_{uuid.uuid4().hex[:8]}",
        run_id=run_id,
        paper_order_id=order_id,
        event_type=event_type,
        severity=severity,
        message=message
    )

def build_paper_audit_timeline(events: list[PaperAuditEvent]) -> list[dict]:
    return [e.dict() for e in events]

def redact_paper_audit_event(event: PaperAuditEvent) -> dict:
    return event.dict(exclude={"metadata"})

def validate_paper_audit_event(event: PaperAuditEvent, config: AppConfig) -> None:
    pass
