import uuid
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from .models import BacktestEvent, BacktestEventType


class BacktestEventBus:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self._events: list[BacktestEvent] = []

    def emit(
        self,
        event_type: BacktestEventType,
        symbol: str | None,
        open_time: int | None,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> BacktestEvent:
        event = BacktestEvent(
            event_id=str(uuid.uuid4()),
            run_id=self.run_id,
            event_type=event_type,
            symbol=symbol,
            open_time=open_time,
            event_time=open_time if open_time else 0,
            message=message,
            metadata=metadata,
            created_at_utc=datetime.now(UTC).isoformat(),
        )
        self._events.append(event)
        return event

    def list_events(self) -> list[BacktestEvent]:
        return list(self._events)

    def filter_events(
        self, event_type: BacktestEventType | None = None, symbol: str | None = None
    ) -> list[BacktestEvent]:
        events = self._events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if symbol:
            events = [e for e in events if e.symbol == symbol]
        return events

    def validate_events(self) -> None:
        pass

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([e.model_dump() for e in self._events])
