import uuid
from datetime import datetime, timezone
from typing import Optional, Any
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperFill, PaperEventType
from binance50.core.exceptions import PaperEventError

class PaperExecutionEvent(BaseModel):
    event_id: str
    event_type: str
    paper_order_id: Optional[str] = None
    paper_fill_id: Optional[str] = None
    symbol: Optional[str] = None
    status: Optional[str] = None
    event_time_utc: datetime
    payload: dict[str, Any]
    correlation_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)

def build_paper_event(event_type: str, order: PaperOrder = None, fill: PaperFill = None, payload: dict = None, config: AppConfig = None) -> PaperExecutionEvent:
    return PaperExecutionEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        paper_order_id=order.paper_order_id if order else None,
        paper_fill_id=fill.paper_fill_id if fill else None,
        symbol=order.symbol if order else (fill.symbol if fill else None),
        status=order.status.value if order else None,
        event_time_utc=datetime.now(timezone.utc),
        payload=payload or {},
        correlation_id=order.correlation_id if order else "unknown"
    )

def emit_paper_order_event(order: PaperOrder, event_type: str, config: AppConfig) -> PaperExecutionEvent:
    return build_paper_event(event_type, order=order, payload=order.dict(), config=config)

def emit_paper_fill_event(fill: PaperFill, order: PaperOrder, config: AppConfig) -> PaperExecutionEvent:
    return build_paper_event("paper_order_filled_local", order=order, fill=fill, payload=fill.dict(), config=config)

def validate_paper_event(event: PaperExecutionEvent, config: AppConfig) -> None:
    if config.paper_execution.events.exchange_execution_report_forbidden:
        if "executionReport" in event.payload or "clientOrderId" in event.payload:
            raise PaperEventError("Exchange execution report format is forbidden in paper events")

def redact_paper_event(event: PaperExecutionEvent) -> dict:
    return event.dict(exclude={"metadata"})
