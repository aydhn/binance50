import pytest

from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamType
from binance50.streams.stream_names import (
    build_stream_name,
    parse_stream_name,
)


def test_build_kline():
    name = build_stream_name("BTCUSDT", StreamType.kline, interval="1m")
    assert name == "btcusdt@kline_1m"

def test_build_book_ticker():
    name = build_stream_name("BTCUSDT", StreamType.book_ticker)
    assert name == "btcusdt@bookTicker"

def test_build_invalid_interval():
    with pytest.raises(ValueError):
        build_stream_name("BTCUSDT", StreamType.kline, interval="99m")

def test_build_mark_price_spot_fails():
    with pytest.raises(ValueError):
        build_stream_name("BTCUSDT", StreamType.mark_price, market_scope=MarketScope.SPOT)

def test_parse_stream_name():
    p1 = parse_stream_name("btcusdt@kline_1m")
    assert p1["symbol"] == "BTCUSDT"
    assert p1["type"] == StreamType.kline
    assert p1["interval"] == "1m"

    p2 = parse_stream_name("ethusdt@bookTicker")
    assert p2["symbol"] == "ETHUSDT"
    assert p2["type"] == StreamType.book_ticker
