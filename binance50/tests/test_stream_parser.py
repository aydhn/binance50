from decimal import Decimal

from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamSource
from binance50.streams.models import BookTickerStreamEvent, KlineStreamEvent
from binance50.streams.parser import parse_combined_stream_payload, parse_stream_payload


def test_parse_kline():
    raw = {
        "e": "kline",
        "E": 1672531260000,
        "s": "BTCUSDT",
        "k": {
            "t": 1672531200000,
            "T": 1672531259999,
            "s": "BTCUSDT",
            "i": "1m",
            "f": 100,
            "L": 200,
            "o": "16500.00",
            "c": "16510.00",
            "h": "16515.00",
            "l": "16490.00",
            "v": "10.5",
            "n": 100,
            "x": True,
            "q": "173355.00",
            "V": "5.0",
            "Q": "82550.00",
            "B": "0",
        },
    }
    res = parse_stream_payload(raw, MarketScope.SPOT, StreamSource.fixture)
    assert res.success
    assert isinstance(res.event, KlineStreamEvent)
    assert res.event.close == Decimal("16510.00")
    assert res.event.is_closed is True


def test_parse_combined():
    raw = {
        "stream": "btcusdt@bookTicker",
        "data": {
            "u": 400900217,
            "s": "BTCUSDT",
            "b": "25201.00",
            "B": "31.21",
            "a": "25202.00",
            "A": "40.66",
            "e": "bookTicker",
            "E": 1672531260000,
        },
    }
    res = parse_combined_stream_payload(raw, MarketScope.SPOT, StreamSource.fixture)
    assert res.success
    assert isinstance(res.event, BookTickerStreamEvent)
    assert res.event.symbol == "BTCUSDT"
    assert res.event.raw_stream_name == "btcusdt@bookTicker"


def test_parse_missing_fields():
    raw = {"e": "kline", "E": 1000}
    res = parse_stream_payload(raw, MarketScope.SPOT, StreamSource.fixture)
    assert not res.success
    assert "Missing 'k'" in res.error
