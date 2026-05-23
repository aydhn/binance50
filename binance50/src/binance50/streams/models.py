from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamEventStatus, StreamSource, StreamType


class StreamEvent(BaseModel):
    event_id: str
    stream_type: StreamType
    source: StreamSource
    symbol: str
    market_scope: MarketScope
    event_time_ms: int
    received_time_ms: int
    raw_stream_name: str
    raw_payload: dict[str, Any]
    status: StreamEventStatus = StreamEventStatus.valid
    warnings: list[str] = Field(default_factory=list)
    correlation_id: str | None = None

    def dump_redacted(self) -> dict[str, Any]:
        """Dump with sensitive fields removed (though public streams usually don't have secrets)"""
        d = self.model_dump()
        return d


class KlineStreamEvent(StreamEvent):
    interval: str
    open_time: int
    close_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quote_volume: Decimal
    number_of_trades: int
    taker_buy_base_volume: Decimal
    taker_buy_quote_volume: Decimal
    is_closed: bool


class BookTickerStreamEvent(StreamEvent):
    bid_price: Decimal
    bid_qty: Decimal
    ask_price: Decimal
    ask_qty: Decimal
    spread_bps: float | None = None


class MiniTickerStreamEvent(StreamEvent):
    close_price: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    total_traded_base_volume: Decimal
    total_traded_quote_volume: Decimal


class TickerStreamEvent(StreamEvent):
    price_change: Decimal
    price_change_percent: Decimal
    weighted_avg_price: Decimal
    last_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    open_time: int
    close_time: int
    trade_count: int


class TradeStreamEvent(StreamEvent):
    trade_id: int
    price: Decimal
    quantity: Decimal
    buyer_order_id: int
    seller_order_id: int
    trade_time_ms: int
    is_buyer_market_maker: bool


class AggTradeStreamEvent(StreamEvent):
    aggregate_trade_id: int
    price: Decimal
    quantity: Decimal
    first_trade_id: int
    last_trade_id: int
    trade_time_ms: int
    is_buyer_market_maker: bool


class DepthUpdateStreamEvent(StreamEvent):
    first_update_id: int
    final_update_id: int
    previous_final_update_id: int | None = None
    bids: list[tuple[Decimal, Decimal]]
    asks: list[tuple[Decimal, Decimal]]


class MarkPriceStreamEvent(StreamEvent):
    mark_price: Decimal
    index_price: Decimal
    estimated_settle_price: Decimal
    funding_rate: Decimal
    next_funding_time: int


class StreamParseResult(BaseModel):
    success: bool
    event: StreamEvent | None = None
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)
    raw_payload_hash: str | None = None


class StreamBatch(BaseModel):
    batch_id: str
    events: list[StreamEvent]
    created_at_utc: datetime
    source: StreamSource
    metadata: dict[str, Any] = Field(default_factory=dict)
