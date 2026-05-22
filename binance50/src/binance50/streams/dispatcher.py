import contextlib
from collections.abc import Callable

from pydantic import BaseModel, Field

from binance50.streams.event_types import StreamType
from binance50.streams.models import StreamEvent


class StreamDispatchResult(BaseModel):
    event_id: str
    stream_type: StreamType
    handled: bool
    handler_name: str | None = None
    success: bool
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)

class StreamDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[StreamType, list[Callable]] = {}

    def register_handler(self, stream_type: StreamType, handler: Callable) -> None:
        if stream_type not in self._handlers:
            self._handlers[stream_type] = []
        self._handlers[stream_type].append(handler)

    def unregister_handler(self, stream_type: StreamType, handler: Callable | None = None) -> None:
        if stream_type in self._handlers:
            if handler:
                with contextlib.suppress(ValueError):
                    self._handlers[stream_type].remove(handler)
            else:
                self._handlers[stream_type].clear()

    def dispatch(self, event: StreamEvent) -> StreamDispatchResult:
        handlers = self._handlers.get(event.stream_type, [])
        if not handlers:
            return StreamDispatchResult(
                event_id=event.event_id,
                stream_type=event.stream_type,
                handled=False,
                success=True,
                warnings=["No handler registered for stream type"]
            )

        # For Phase 9, we assume single handler or simple iteration without complex threading.
        # We only dispatch to passive consumers like realtime_store.

        last_success = True
        last_error = None
        handler_name = None

        for handler in handlers:
            handler_name = handler.__name__ if hasattr(handler, "__name__") else str(handler)
            try:
                handler(event)
            except Exception as e:
                last_success = False
                last_error = f"Handler {handler_name} failed: {str(e)}"
                break # stop on first failure for now

        return StreamDispatchResult(
            event_id=event.event_id,
            stream_type=event.stream_type,
            handled=True,
            handler_name=handler_name,
            success=last_success,
            error=last_error
        )

    def dispatch_batch(self, events: list[StreamEvent]) -> list[StreamDispatchResult]:
        results = []
        for event in events:
            results.append(self.dispatch(event))
        return results
