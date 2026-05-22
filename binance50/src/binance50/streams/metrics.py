from datetime import datetime

from pydantic import BaseModel, Field

from binance50.core.time_utils import get_utc_now
from binance50.streams.buffer import StreamBufferDecision
from binance50.streams.dispatcher import StreamDispatchResult
from binance50.streams.models import StreamParseResult


class StreamMetricsSnapshot(BaseModel):
    total_events: int = 0
    parsed_events: int = 0
    invalid_events: int = 0
    stale_events: int = 0
    duplicate_events: int = 0
    buffer_overflows: int = 0
    avg_lag_ms: float = 0.0
    max_lag_ms: int = 0
    events_by_type: dict[str, int] = Field(default_factory=dict)
    events_by_symbol: dict[str, int] = Field(default_factory=dict)
    generated_at_utc: datetime = Field(default_factory=get_utc_now)

class StreamMetricsCollector:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._total_events = 0
        self._parsed_events = 0
        self._invalid_events = 0
        self._stale_events = 0
        self._duplicate_events = 0
        self._buffer_overflows = 0

        self._total_lag_ms = 0
        self._max_lag_ms = 0
        self._lag_count = 0

        self._events_by_type: dict[str, int] = {}
        self._events_by_symbol: dict[str, int] = {}

    def record_parse_result(self, result: StreamParseResult) -> None:
        self._total_events += 1
        if result.success and result.event:
            self._parsed_events += 1
            st = result.event.stream_type.value
            sym = result.event.symbol

            self._events_by_type[st] = self._events_by_type.get(st, 0) + 1
            self._events_by_symbol[sym] = self._events_by_symbol.get(sym, 0) + 1

            # Record lag if event has valid time
            if result.event.event_time_ms > 0:
                lag = max(0, result.event.received_time_ms - result.event.event_time_ms)
                self._total_lag_ms += lag
                self._lag_count += 1
                if lag > self._max_lag_ms:
                    self._max_lag_ms = lag

        else:
            self._invalid_events += 1

    def record_buffer_decision(self, decision: StreamBufferDecision) -> None:
        if decision.dropped and decision.reason == "duplicate_event":
            self._duplicate_events += 1
        elif decision.dropped and "buffer_full" in str(decision.reason):
            self._buffer_overflows += 1

        if decision.event_status.value == "stale":
            self._stale_events += 1

    def record_dispatch_result(self, result: StreamDispatchResult) -> None:
        pass # Optional tracking for dispatch metrics

    def snapshot(self) -> StreamMetricsSnapshot:
        avg_lag = (self._total_lag_ms / self._lag_count) if self._lag_count > 0 else 0.0
        return StreamMetricsSnapshot(
            total_events=self._total_events,
            parsed_events=self._parsed_events,
            invalid_events=self._invalid_events,
            stale_events=self._stale_events,
            duplicate_events=self._duplicate_events,
            buffer_overflows=self._buffer_overflows,
            avg_lag_ms=round(avg_lag, 2),
            max_lag_ms=self._max_lag_ms,
            events_by_type=self._events_by_type.copy(),
            events_by_symbol=self._events_by_symbol.copy(),
            generated_at_utc=get_utc_now()
        )
