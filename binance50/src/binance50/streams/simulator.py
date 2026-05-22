from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.streams.buffer import StreamBuffer, StreamBufferDecision
from binance50.streams.event_types import StreamSource
from binance50.streams.metrics import StreamMetricsCollector
from binance50.streams.models import StreamEvent
from binance50.streams.parser import parse_stream_payload
from binance50.streams.validators import validate_stream_event


class StreamSimulationResult(BaseModel):
    simulation_id: str
    source: StreamSource
    event_count: int = 0
    accepted_count: int = 0
    dropped_count: int = 0
    invalid_count: int = 0
    metrics: dict = Field(default_factory=dict)
    buffer_report: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

class StreamSimulator:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def load_fixture_events(self, fixture_names: list[str], market_scope: MarketScope) -> list[StreamEvent]:
        from binance50.streams.fixtures import load_stream_fixture_sequence
        raw_events = load_stream_fixture_sequence(fixture_names)

        parsed = []
        for raw in raw_events:
            # Assume fixture=True is in metadata or just treat as fixture
            res = parse_stream_payload(raw, market_scope, StreamSource.fixture)
            if res.success and res.event:
                validated = validate_stream_event(res.event, self.config)
                parsed.append(validated)
        return parsed

    def emit_events(
        self,
        events: list[StreamEvent],
        buffer: StreamBuffer,
        metrics: StreamMetricsCollector | None = None
    ) -> list[StreamBufferDecision]:

        decisions = []
        for event in events:
            decision = buffer.push(event)
            decisions.append(decision)
            if metrics:
                metrics.record_buffer_decision(decision)
        return decisions

    def simulate_from_fixtures(
        self,
        fixture_names: list[str],
        market_scope: MarketScope,
        buffer: StreamBuffer | None = None,
        metrics: StreamMetricsCollector | None = None
    ) -> StreamSimulationResult:

        if buffer is None:
            buffer = StreamBuffer(max_events=self.config.streams.buffer_max_events, drop_policy=self.config.streams.buffer_drop_policy)
        if metrics is None:
            metrics = StreamMetricsCollector()

        from binance50.core.time_utils import get_utc_now
        from binance50.streams.fixtures import load_stream_fixture_sequence

        raw_events = load_stream_fixture_sequence(fixture_names)

        invalid_count = 0
        accepted_count = 0
        dropped_count = 0

        for raw in raw_events:
            res = parse_stream_payload(raw, market_scope, StreamSource.fixture)
            metrics.record_parse_result(res)

            if not res.success or not res.event:
                invalid_count += 1
                continue

            validated = validate_stream_event(res.event, self.config)
            decision = buffer.push(validated)
            metrics.record_buffer_decision(decision)

            if decision.accepted:
                accepted_count += 1
            else:
                dropped_count += 1

        return StreamSimulationResult(
            simulation_id=f"sim_{int(get_utc_now().timestamp())}",
            source=StreamSource.fixture,
            event_count=len(raw_events),
            accepted_count=accepted_count,
            dropped_count=dropped_count,
            invalid_count=invalid_count,
            metrics=metrics.snapshot().model_dump(),
            buffer_report=buffer.to_report()
        )
