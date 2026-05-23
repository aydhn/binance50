from binance50.core.enums import MarketScope
from binance50.streams.buffer import StreamBuffer
from binance50.streams.event_types import StreamSource, StreamType
from binance50.streams.models import StreamEvent


def _make_event(eid: str) -> StreamEvent:
    return StreamEvent(
        event_id=eid,
        stream_type=StreamType.unknown,
        source=StreamSource.mock,
        symbol="BTC",
        market_scope=MarketScope.SPOT,
        event_time_ms=0,
        received_time_ms=0,
        raw_stream_name="test",
        raw_payload={},
    )


def test_buffer_push_pop():
    buf = StreamBuffer(max_events=10)
    e = _make_event("1")
    dec = buf.push(e)
    assert dec.accepted
    assert buf.size() == 1

    out = buf.pop()
    assert out.event_id == "1"
    assert buf.size() == 0


def test_buffer_overflow_reject():
    buf = StreamBuffer(max_events=2, drop_policy="reject_new")
    buf.push(_make_event("1"))
    buf.push(_make_event("2"))
    dec = buf.push(_make_event("3"))

    assert not dec.accepted
    assert dec.dropped
    assert dec.reason == "buffer_full"
    assert buf.size() == 2


def test_buffer_duplicate():
    buf = StreamBuffer(max_events=10)
    buf.push(_make_event("1"))
    dec = buf.push(_make_event("1"))

    assert not dec.accepted
    assert dec.reason == "duplicate_event"
    assert buf.size() == 1
