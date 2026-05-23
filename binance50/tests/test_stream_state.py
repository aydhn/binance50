from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamSource, StreamType
from binance50.streams.models import StreamEvent
from binance50.streams.state import StreamStateStore


def test_stream_state():
    store = StreamStateStore()
    e = StreamEvent(
        event_id="1",
        stream_type=StreamType.unknown,
        source=StreamSource.mock,
        symbol="BTCUSDT",
        market_scope=MarketScope.SPOT,
        event_time_ms=1000,
        received_time_ms=1010,
        raw_stream_name="x",
        raw_payload={},
    )
    store.update(e)
    st = store.get_symbol_state("BTCUSDT")
    assert st is not None
    assert st.event_count == 1
    assert st.last_event_time_ms == 1000

    rep = store.to_report()
    assert rep["tracked_symbols"] == 1
