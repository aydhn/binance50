import time

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.streams.dispatcher import StreamDispatcher
from binance50.streams.event_types import StreamSource
from binance50.streams.models import StreamEvent
from binance50.streams.simulator import StreamSimulator


class StreamReplayResult(BaseModel):
    replay_id: str
    event_count: int = 0
    dispatched_count: int = 0
    failed_count: int = 0
    duration_simulated_ms: int = 0
    duration_wall_ms: int = 0
    speed_multiplier: float
    warnings: list[str] = Field(default_factory=list)

class StreamReplayEngine:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def replay_events(
        self,
        events: list[StreamEvent],
        speed_multiplier: float,
        dispatcher: StreamDispatcher | None = None
    ) -> StreamReplayResult:
        from binance50.core.time_utils import get_utc_now

        if speed_multiplier <= 0:
            raise ValueError("Speed multiplier must be > 0")

        if not events:
            return StreamReplayResult(
                replay_id=f"rep_{int(get_utc_now().timestamp())}",
                speed_multiplier=speed_multiplier,
                warnings=["No events to replay"]
            )

        events = sorted(events, key=lambda e: e.event_time_ms)

        simulated_start = events[0].event_time_ms
        simulated_end = events[-1].event_time_ms
        simulated_duration = simulated_end - simulated_start

        wall_start = time.perf_counter_ns()

        dispatched_count = 0
        failed_count = 0

        # We do not sleep in tests unless specifically requested. Here we just process sequentially.
        for event in events:
            event.source = StreamSource.replay
            if dispatcher:
                res = dispatcher.dispatch(event)
                if res.success:
                    dispatched_count += 1
                else:
                    failed_count += 1
            else:
                # No dispatcher means just loop
                dispatched_count += 1

        wall_end = time.perf_counter_ns()
        wall_duration_ms = (wall_end - wall_start) // 1_000_000

        return StreamReplayResult(
            replay_id=f"rep_{int(get_utc_now().timestamp())}",
            event_count=len(events),
            dispatched_count=dispatched_count,
            failed_count=failed_count,
            duration_simulated_ms=simulated_duration,
            duration_wall_ms=wall_duration_ms,
            speed_multiplier=speed_multiplier
        )

    def replay_fixture_sequence(
        self,
        fixture_names: list[str],
        market_scope: MarketScope,
        speed_multiplier: float,
        dispatcher: StreamDispatcher | None = None
    ) -> StreamReplayResult:
        sim = StreamSimulator(self.config)
        events = sim.load_fixture_events(fixture_names, market_scope)
        return self.replay_events(events, speed_multiplier, dispatcher)
