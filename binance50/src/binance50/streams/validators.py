from binance50.config.models import AppConfig
from binance50.core.time_utils import get_current_time_ms
from binance50.streams.event_types import StreamEventStatus, StreamType
from binance50.streams.models import (
    BookTickerStreamEvent,
    DepthUpdateStreamEvent,
    KlineStreamEvent,
    StreamEvent,
)


def compute_event_lag_ms(event: StreamEvent, now_ms: int | None = None) -> int | None:
    if event.event_time_ms == 0:
        return None
    if not now_ms:
        now_ms = get_current_time_ms()
    return max(0, now_ms - event.event_time_ms)

def is_event_stale(event: StreamEvent, config: AppConfig, now_ms: int | None = None) -> bool:
    lag = compute_event_lag_ms(event, now_ms)
    if lag is None:
        return False
    return lag > (config.streams.stale_event_threshold_seconds * 1000)

def validate_event_time(event: StreamEvent, config: AppConfig, now_ms: int | None = None) -> list[str]:
    warnings = []
    if not now_ms:
        now_ms = get_current_time_ms()

    # Check if event time is in the future
    if event.event_time_ms > now_ms + config.streams.max_event_time_skew_ms:
        warnings.append(f"Event time {event.event_time_ms} is too far in the future (skew threshold: {config.streams.max_event_time_skew_ms}ms)")

    return warnings

def validate_kline_event(event: KlineStreamEvent) -> list[str]:
    warnings = []
    if event.high < event.low:
        warnings.append("Kline high < low")
    if event.open > event.high or event.open < event.low:
        warnings.append("Kline open not within high/low range")
    if event.close > event.high or event.close < event.low:
        warnings.append("Kline close not within high/low range")
    if event.volume < 0:
        warnings.append("Kline volume < 0")
    return warnings

def validate_book_ticker_event(event: BookTickerStreamEvent) -> list[str]:
    warnings = []
    if event.ask_price < event.bid_price and event.ask_price > 0 and event.bid_price > 0:
        warnings.append("BookTicker ask < bid (crossed book)")
    return warnings

def validate_depth_update_event(event: DepthUpdateStreamEvent) -> list[str]:
    warnings = []
    for p, q in event.bids:
        if p < 0 or q < 0:
            warnings.append("DepthUpdate negative bid price/qty")
            break
    for p, q in event.asks:
        if p < 0 or q < 0:
            warnings.append("DepthUpdate negative ask price/qty")
            break
    if event.final_update_id < event.first_update_id:
         warnings.append("DepthUpdate final update id < first update id")
    return warnings

def validate_stream_event(event: StreamEvent, config: AppConfig) -> StreamEvent:
    if event.status != StreamEventStatus.valid:
        return event

    warnings = list(event.warnings)
    warnings.extend(validate_event_time(event, config))

    if is_event_stale(event, config):
        event.status = StreamEventStatus.stale
        warnings.append("Event is stale")

    if event.stream_type == StreamType.kline and isinstance(event, KlineStreamEvent):
        warnings.extend(validate_kline_event(event))
    elif event.stream_type == StreamType.book_ticker and isinstance(event, BookTickerStreamEvent):
        warnings.extend(validate_book_ticker_event(event))
    elif event.stream_type in (StreamType.partial_depth, StreamType.diff_depth) and isinstance(event, DepthUpdateStreamEvent):
        warnings.extend(validate_depth_update_event(event))

    if warnings and event.status == StreamEventStatus.valid:
        # Don't upgrade status if we only have simple validation warnings,
        # unless they are critical. Here we treat them as warnings.
        event.warnings = warnings
        # Could set status to warning, but staying valid with warnings list is fine.

    return event
