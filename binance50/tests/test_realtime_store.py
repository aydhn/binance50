from decimal import Decimal

from binance50.core.enums import MarketScope
from binance50.market_data.realtime_store import RealtimeMarketDataStore
from binance50.streams.event_types import StreamSource, StreamType
from binance50.streams.models import BookTickerStreamEvent


def test_realtime_store():
    store = RealtimeMarketDataStore()
    e = BookTickerStreamEvent(
        event_id="1", stream_type=StreamType.book_ticker, source=StreamSource.mock,
        symbol="BTCUSDT", market_scope=MarketScope.SPOT, event_time_ms=0,
        received_time_ms=0, raw_stream_name="x", raw_payload={},
        bid_price=Decimal("10"), bid_qty=Decimal("1"),
        ask_price=Decimal("11"), ask_qty=Decimal("1")
    )
    store.update_from_event(e)

    b = store.get_latest_book_ticker("BTCUSDT")
    assert b is not None
    assert b.bid_price == Decimal("10")

    syms = store.list_symbols()
    assert "BTCUSDT" in syms

    store.clear()
    assert len(store.list_symbols()) == 0
