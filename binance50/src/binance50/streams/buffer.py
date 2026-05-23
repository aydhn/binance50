from collections import deque
from threading import Lock
from typing import Literal

from pydantic import BaseModel

from binance50.streams.event_types import StreamEventStatus
from binance50.streams.models import StreamEvent


class StreamBufferDecision(BaseModel):
    accepted: bool
    dropped: bool
    reason: str | None = None
    buffer_size: int
    usage_pct: float
    event_status: StreamEventStatus
    warnings: list[str]


class StreamBuffer:
    def __init__(
        self,
        max_events: int = 10000,
        drop_policy: Literal["reject_new", "drop_oldest", "drop_newest"] = "reject_new",
        warn_threshold_pct: float = 80.0,
        detect_duplicates: bool = True,
        duplicate_cache_size: int = 5000,
    ) -> None:
        self.max_events = max_events
        self.drop_policy = drop_policy
        self.warn_threshold_pct = warn_threshold_pct
        self.detect_duplicates = detect_duplicates
        self.duplicate_cache_size = duplicate_cache_size

        self._buffer: deque[StreamEvent] = deque()
        self._duplicate_cache: set[str] = set()
        self._duplicate_queue: deque[str] = deque()
        self._lock = Lock()

    def _check_duplicate(self, event_id: str) -> bool:
        if not self.detect_duplicates:
            return False
        if event_id in self._duplicate_cache:
            return True

        self._duplicate_cache.add(event_id)
        self._duplicate_queue.append(event_id)

        if len(self._duplicate_queue) > self.duplicate_cache_size:
            oldest = self._duplicate_queue.popleft()
            self._duplicate_cache.discard(oldest)

        return False

    def push(self, event: StreamEvent) -> StreamBufferDecision:
        with self._lock:
            # Check duplicate
            if self._check_duplicate(event.event_id):
                event.status = StreamEventStatus.duplicate
                return StreamBufferDecision(
                    accepted=False,
                    dropped=True,
                    reason="duplicate_event",
                    buffer_size=len(self._buffer),
                    usage_pct=self._usage_pct_internal(),
                    event_status=event.status,
                    warnings=["Duplicate event detected"],
                )

            current_size = len(self._buffer)
            if current_size >= self.max_events:
                if self.drop_policy == "reject_new":
                    return StreamBufferDecision(
                        accepted=False,
                        dropped=True,
                        reason="buffer_full",
                        buffer_size=current_size,
                        usage_pct=100.0,
                        event_status=event.status,
                        warnings=["Buffer overflow - reject_new policy"],
                    )
                elif self.drop_policy == "drop_oldest":
                    self._buffer.popleft()
                    self._buffer.append(event)
                    return StreamBufferDecision(
                        accepted=True,
                        dropped=False,
                        reason="buffer_full_drop_oldest",
                        buffer_size=self.max_events,
                        usage_pct=100.0,
                        event_status=event.status,
                        warnings=["Buffer overflow - drop_oldest policy"],
                    )
                else:  # drop_newest
                    self._buffer.pop()
                    self._buffer.append(event)
                    return StreamBufferDecision(
                        accepted=True,
                        dropped=False,
                        reason="buffer_full_drop_newest",
                        buffer_size=self.max_events,
                        usage_pct=100.0,
                        event_status=event.status,
                        warnings=["Buffer overflow - drop_newest policy"],
                    )

            # Normal append
            self._buffer.append(event)
            pct = self._usage_pct_internal()
            warnings = []
            if pct >= self.warn_threshold_pct:
                warnings.append("Buffer threshold warning")

            return StreamBufferDecision(
                accepted=True,
                dropped=False,
                reason=None,
                buffer_size=len(self._buffer),
                usage_pct=pct,
                event_status=event.status,
                warnings=warnings,
            )

    def pop(self) -> StreamEvent | None:
        with self._lock:
            if not self._buffer:
                return None
            return self._buffer.popleft()

    def pop_batch(self, max_items: int) -> list[StreamEvent]:
        with self._lock:
            batch = []
            while self._buffer and len(batch) < max_items:
                batch.append(self._buffer.popleft())
            return batch

    def peek(self) -> StreamEvent | None:
        with self._lock:
            if not self._buffer:
                return None
            return self._buffer[0]

    def size(self) -> int:
        with self._lock:
            return len(self._buffer)

    def capacity(self) -> int:
        return self.max_events

    def _usage_pct_internal(self) -> float:
        if self.max_events == 0:
            return 0.0
        return (len(self._buffer) / self.max_events) * 100.0

    def usage_pct(self) -> float:
        with self._lock:
            return self._usage_pct_internal()

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()
            self._duplicate_cache.clear()
            self._duplicate_queue.clear()

    def to_report(self) -> dict:
        with self._lock:
            return {
                "size": len(self._buffer),
                "capacity": self.max_events,
                "usage_pct": self._usage_pct_internal(),
                "drop_policy": self.drop_policy,
                "warn_threshold_pct": self.warn_threshold_pct,
                "duplicate_cache_size": len(self._duplicate_cache),
            }
