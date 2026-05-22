import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Any

from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamEventStatus, StreamSource, StreamType
from binance50.streams.models import (
    AggTradeStreamEvent,
    BookTickerStreamEvent,
    DepthUpdateStreamEvent,
    KlineStreamEvent,
    MarkPriceStreamEvent,
    MiniTickerStreamEvent,
    StreamParseResult,
    TickerStreamEvent,
    TradeStreamEvent,
)
from binance50.streams.stream_names import parse_stream_name


def safe_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None

def detect_stream_type(payload: dict, stream_name: str | None = None) -> StreamType:
    e_val = payload.get("e")
    if e_val == "kline":
        return StreamType.kline
    elif e_val == "24hrMiniTicker":
        return StreamType.mini_ticker
    elif e_val == "24hrTicker":
        return StreamType.ticker
    elif e_val == "bookTicker":
        return StreamType.book_ticker
    elif e_val == "trade":
        return StreamType.trade
    elif e_val == "aggTrade":
        return StreamType.agg_trade
    elif e_val == "depthUpdate":
        return StreamType.diff_depth # Spot diff depth uses e=depthUpdate
    elif e_val == "markPriceUpdate":
        return StreamType.mark_price

    if stream_name:
        parsed = parse_stream_name(stream_name)
        return parsed.get("type", StreamType.unknown)

    return StreamType.unknown

def parse_combined_stream_payload(payload: dict, market_scope: MarketScope, source: StreamSource = StreamSource.fixture) -> StreamParseResult:
    if "stream" not in payload or "data" not in payload:
        return StreamParseResult(success=False, error="Invalid combined payload format")

    stream_name = payload["stream"]
    data = payload["data"]

    return parse_stream_payload(data, market_scope, source, stream_name=stream_name)

def parse_stream_payload(payload: dict, market_scope: MarketScope, source: StreamSource = StreamSource.fixture, stream_name: str | None = None) -> StreamParseResult:
    if "stream" in payload and "data" in payload:
        return parse_combined_stream_payload(payload, market_scope, source)

    raw_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    try:
        stream_type = detect_stream_type(payload, stream_name)
        if stream_type == StreamType.unknown:
            return StreamParseResult(success=False, error="Unknown stream type", raw_payload_hash=raw_hash, warnings=["Unknown stream type detected"])

        if stream_type == StreamType.kline:
            event = parse_kline_event(payload, market_scope, source)
        elif stream_type == StreamType.book_ticker:
            event = parse_book_ticker_event(payload, market_scope, source)
        elif stream_type == StreamType.mini_ticker:
            event = parse_mini_ticker_event(payload, market_scope, source)
        elif stream_type == StreamType.ticker:
            event = parse_ticker_event(payload, market_scope, source)
        elif stream_type == StreamType.trade:
            event = parse_trade_event(payload, market_scope, source)
        elif stream_type == StreamType.agg_trade:
            event = parse_agg_trade_event(payload, market_scope, source)
        elif stream_type in (StreamType.partial_depth, StreamType.diff_depth):
            event = parse_depth_update_event(payload, market_scope, source)
        elif stream_type == StreamType.mark_price:
            event = parse_mark_price_event(payload, market_scope, source)
        else:
            return StreamParseResult(success=False, error=f"Parser not implemented for {stream_type}", raw_payload_hash=raw_hash)

        if stream_name:
            event.raw_stream_name = stream_name

        return StreamParseResult(success=True, event=event, raw_payload_hash=raw_hash)
    except Exception as e:
        return StreamParseResult(success=False, error=f"Parse exception: {str(e)}", raw_payload_hash=raw_hash)

def _get_base_event_fields(payload: dict, stream_type: StreamType, market_scope: MarketScope, source: StreamSource) -> dict:
    from binance50.core.time_utils import get_current_time_ms

    # "s" is common for symbol. If not present (e.g. some bookTickers), try other fields or rely on caller to patch.
    symbol = payload.get("s", "UNKNOWN").upper()
    event_time_ms = int(payload.get("E", get_current_time_ms()))

    # BookTicker special case, might not have E
    if "E" not in payload and "u" in payload and stream_type == StreamType.book_ticker:
        # Just use current time if event time missing
        event_time_ms = get_current_time_ms()

    return {
        "event_id": f"{stream_type.value}_{symbol}_{event_time_ms}_{payload.get('u', 0)}",
        "stream_type": stream_type,
        "source": source,
        "symbol": symbol,
        "market_scope": market_scope,
        "event_time_ms": event_time_ms,
        "received_time_ms": get_current_time_ms(),
        "raw_stream_name": "unknown",
        "raw_payload": payload,
        "status": StreamEventStatus.valid
    }

def parse_kline_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> KlineStreamEvent:
    base = _get_base_event_fields(payload, StreamType.kline, market_scope, source)
    if "k" not in payload:
        raise ValueError("Missing 'k' field in kline event")
    k = payload["k"]

    return KlineStreamEvent(
        **base,
        interval=k["i"],
        open_time=int(k["t"]),
        close_time=int(k["T"]),
        open=safe_decimal(k["o"]),
        high=safe_decimal(k["h"]),
        low=safe_decimal(k["l"]),
        close=safe_decimal(k["c"]),
        volume=safe_decimal(k["v"]),
        quote_volume=safe_decimal(k["q"]),
        number_of_trades=int(k["n"]),
        taker_buy_base_volume=safe_decimal(k["V"]),
        taker_buy_quote_volume=safe_decimal(k["Q"]),
        is_closed=bool(k["x"])
    )

def parse_book_ticker_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> BookTickerStreamEvent:
    base = _get_base_event_fields(payload, StreamType.book_ticker, market_scope, source)

    bid = safe_decimal(payload.get("b"))
    ask = safe_decimal(payload.get("a"))

    if bid is None or ask is None:
         raise ValueError("Missing bid/ask fields in book_ticker event")

    spread = None
    if ask > 0 and bid > 0:
        spread = float((ask - bid) / ask * 10000)

    return BookTickerStreamEvent(
        **base,
        bid_price=bid,
        bid_qty=safe_decimal(payload.get("B", 0)),
        ask_price=ask,
        ask_qty=safe_decimal(payload.get("A", 0)),
        spread_bps=spread
    )

def parse_mini_ticker_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> MiniTickerStreamEvent:
    base = _get_base_event_fields(payload, StreamType.mini_ticker, market_scope, source)
    return MiniTickerStreamEvent(
        **base,
        close_price=safe_decimal(payload["c"]),
        open_price=safe_decimal(payload["o"]),
        high_price=safe_decimal(payload["h"]),
        low_price=safe_decimal(payload["l"]),
        total_traded_base_volume=safe_decimal(payload["v"]),
        total_traded_quote_volume=safe_decimal(payload["q"])
    )

def parse_ticker_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> TickerStreamEvent:
    base = _get_base_event_fields(payload, StreamType.ticker, market_scope, source)
    return TickerStreamEvent(
        **base,
        price_change=safe_decimal(payload["p"]),
        price_change_percent=safe_decimal(payload["P"]),
        weighted_avg_price=safe_decimal(payload["w"]),
        last_price=safe_decimal(payload["c"]),
        volume=safe_decimal(payload["v"]),
        quote_volume=safe_decimal(payload["q"]),
        open_time=int(payload.get("O", 0)),
        close_time=int(payload.get("C", 0)),
        trade_count=int(payload.get("n", 0))
    )

def parse_trade_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> TradeStreamEvent:
    base = _get_base_event_fields(payload, StreamType.trade, market_scope, source)
    return TradeStreamEvent(
        **base,
        trade_id=int(payload["t"]),
        price=safe_decimal(payload["p"]),
        quantity=safe_decimal(payload["q"]),
        buyer_order_id=int(payload["b"]),
        seller_order_id=int(payload["a"]),
        trade_time_ms=int(payload["T"]),
        is_buyer_market_maker=bool(payload["m"])
    )

def parse_agg_trade_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> AggTradeStreamEvent:
    base = _get_base_event_fields(payload, StreamType.agg_trade, market_scope, source)
    return AggTradeStreamEvent(
        **base,
        aggregate_trade_id=int(payload["a"]),
        price=safe_decimal(payload["p"]),
        quantity=safe_decimal(payload["q"]),
        first_trade_id=int(payload["f"]),
        last_trade_id=int(payload["l"]),
        trade_time_ms=int(payload["T"]),
        is_buyer_market_maker=bool(payload["m"])
    )

def parse_depth_update_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> DepthUpdateStreamEvent:
    base = _get_base_event_fields(payload, StreamType.diff_depth, market_scope, source)

    bids = [(safe_decimal(p), safe_decimal(q)) for p, q in payload.get("b", [])]
    asks = [(safe_decimal(p), safe_decimal(q)) for p, q in payload.get("a", [])]

    return DepthUpdateStreamEvent(
        **base,
        first_update_id=int(payload.get("U", 0)),
        final_update_id=int(payload.get("u", 0)),
        previous_final_update_id=int(payload.get("pu", 0)) if "pu" in payload else None,
        bids=bids,
        asks=asks
    )

def parse_mark_price_event(payload: dict, market_scope: MarketScope, source: StreamSource) -> MarkPriceStreamEvent:
    base = _get_base_event_fields(payload, StreamType.mark_price, market_scope, source)
    return MarkPriceStreamEvent(
        **base,
        mark_price=safe_decimal(payload["p"]),
        index_price=safe_decimal(payload["i"]),
        estimated_settle_price=safe_decimal(payload["P"]),
        funding_rate=safe_decimal(payload["r"]),
        next_funding_time=int(payload["T"])
    )
