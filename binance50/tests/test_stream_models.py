from decimal import Decimal

from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamSource, StreamType
from binance50.streams.models import BookTickerStreamEvent, KlineStreamEvent, MarkPriceStreamEvent


def test_kline_event():
    k = KlineStreamEvent(
        event_id="test",
        stream_type=StreamType.kline,
        source=StreamSource.fixture,
        symbol="BTCUSDT",
        market_scope=MarketScope.SPOT,
        event_time_ms=100,
        received_time_ms=110,
        raw_stream_name="test",
        raw_payload={},
        interval="1m",
        open_time=0,
        close_time=59999,
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("10"),
        quote_volume=Decimal("1000"),
        number_of_trades=5,
        taker_buy_base_volume=Decimal("5"),
        taker_buy_quote_volume=Decimal("500"),
        is_closed=True
    )
    assert k.is_closed
    d = k.dump_redacted()
    assert "event_id" in d

def test_book_ticker_event():
    b = BookTickerStreamEvent(
        event_id="test",
        stream_type=StreamType.book_ticker,
        source=StreamSource.fixture,
        symbol="BTCUSDT",
        market_scope=MarketScope.SPOT,
        event_time_ms=100,
        received_time_ms=110,
        raw_stream_name="test",
        raw_payload={},
        bid_price=Decimal("100.0"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("101.0"),
        ask_qty=Decimal("2"),
        spread_bps=100.0
    )
    assert b.spread_bps == 100.0

def test_mark_price_event():
    m = MarkPriceStreamEvent(
        event_id="test",
        stream_type=StreamType.mark_price,
        source=StreamSource.fixture,
        symbol="BTCUSDT",
        market_scope=MarketScope.USDM_FUTURES,
        event_time_ms=100,
        received_time_ms=110,
        raw_stream_name="test",
        raw_payload={},
        mark_price=Decimal("100"),
        index_price=Decimal("100"),
        estimated_settle_price=Decimal("100"),
        funding_rate=Decimal("0.01"),
        next_funding_time=200
    )
    assert m.funding_rate == Decimal("0.01")
