from typing import Any

from pydantic import BaseModel, Field

from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamEventStatus, StreamType
from binance50.streams.models import (
    BookTickerStreamEvent,
    KlineStreamEvent,
    StreamEvent,
    TickerStreamEvent,
)


class SymbolStreamState(BaseModel):
    symbol: str
    market_scope: MarketScope
    last_event_time_ms: int = 0
    last_received_time_ms: int = 0
    last_kline_open_time_by_interval: dict[str, int] = Field(default_factory=dict)
    last_book_ticker: dict[str, Any] | None = None
    last_ticker: dict[str, Any] | None = None
    event_count: int = 0
    stale_count: int = 0
    duplicate_count: int = 0
    parse_error_count: int = 0
    warnings: list[str] = Field(default_factory=list)

class StreamStateStore:
    def __init__(self) -> None:
        self._states: dict[str, SymbolStreamState] = {}

    def _get_or_create(self, symbol: str, market_scope: MarketScope) -> SymbolStreamState:
        if symbol not in self._states:
            self._states[symbol] = SymbolStreamState(symbol=symbol, market_scope=market_scope)
        return self._states[symbol]

    def update(self, event: StreamEvent) -> None:
        state = self._get_or_create(event.symbol, event.market_scope)

        state.event_count += 1

        if event.status == StreamEventStatus.stale:
            state.stale_count += 1
        elif event.status == StreamEventStatus.duplicate:
            state.duplicate_count += 1
        elif event.status == StreamEventStatus.invalid:
            state.parse_error_count += 1

        if event.event_time_ms > state.last_event_time_ms:
            state.last_event_time_ms = event.event_time_ms

        if event.received_time_ms > state.last_received_time_ms:
            state.last_received_time_ms = event.received_time_ms

        if event.stream_type == StreamType.kline and isinstance(event, KlineStreamEvent):
            state.last_kline_open_time_by_interval[event.interval] = event.open_time

        elif event.stream_type == StreamType.book_ticker and isinstance(event, BookTickerStreamEvent):
            state.last_book_ticker = {
                "bid": float(event.bid_price),
                "ask": float(event.ask_price),
                "spread_bps": event.spread_bps
            }

        elif event.stream_type == StreamType.ticker and isinstance(event, TickerStreamEvent):
            state.last_ticker = {
                "last_price": float(event.last_price),
                "volume": float(event.volume)
            }

    def get_symbol_state(self, symbol: str) -> SymbolStreamState | None:
        return self._states.get(symbol.upper())

    def list_states(self) -> list[SymbolStreamState]:
        return list(self._states.values())

    def reset(self, symbol: str | None = None) -> None:
        if symbol:
            sym = symbol.upper()
            if sym in self._states:
                del self._states[sym]
        else:
            self._states.clear()

    def to_report(self) -> dict:
        return {
            "tracked_symbols": len(self._states),
            "total_events": sum(s.event_count for s in self._states.values()),
            "total_stale": sum(s.stale_count for s in self._states.values()),
            "total_duplicates": sum(s.duplicate_count for s in self._states.values())
        }
