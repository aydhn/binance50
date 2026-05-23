from binance50.core.enums import MarketScope
from binance50.streams.dispatcher import StreamDispatcher
from binance50.streams.event_types import StreamSource, StreamType
from binance50.streams.models import StreamEvent


def test_dispatcher():
    disp = StreamDispatcher()

    calls = []

    def handler(ev):
        calls.append(ev.event_id)

    disp.register_handler(StreamType.kline, handler)

    e = StreamEvent(
        event_id="123",
        stream_type=StreamType.kline,
        source=StreamSource.mock,
        symbol="BTC",
        market_scope=MarketScope.SPOT,
        event_time_ms=0,
        received_time_ms=0,
        raw_stream_name="x",
        raw_payload={},
    )

    res = disp.dispatch(e)
    assert res.handled
    assert res.success
    assert "123" in calls


def test_dispatcher_unhandled():
    disp = StreamDispatcher()
    e = StreamEvent(
        event_id="123",
        stream_type=StreamType.book_ticker,
        source=StreamSource.mock,
        symbol="BTC",
        market_scope=MarketScope.SPOT,
        event_time_ms=0,
        received_time_ms=0,
        raw_stream_name="x",
        raw_payload={},
    )
    res = disp.dispatch(e)
    assert not res.handled
