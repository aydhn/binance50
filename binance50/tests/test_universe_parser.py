from decimal import Decimal

from binance50.core.enums import MarketScope
from binance50.universe.models import SymbolFilterType, SymbolStatus
from binance50.universe.parser import (
    parse_24h_tickers,
    parse_book_tickers,
    parse_spot_exchange_info,
    parse_usdm_exchange_info,
)


def test_parse_spot_exchange_info():
    payload = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "status": "TRADING",
                "filters": [
                    {"filterType": "PRICE_FILTER", "tickSize": "0.1"},
                    {"filterType": "UNKNOWN_FILTER", "foo": "bar"},
                ],
            }
        ]
    }
    result = parse_spot_exchange_info(payload)
    assert len(result) == 1
    m = result[0]
    assert m.symbol == "BTCUSDT"
    assert m.status == SymbolStatus.TRADING
    assert m.market_scope == MarketScope.SPOT
    assert SymbolFilterType.PRICE_FILTER in m.filters
    assert m.filters[SymbolFilterType.PRICE_FILTER].tick_size == Decimal("0.1")
    assert SymbolFilterType.UNKNOWN in m.filters


def test_parse_usdm_exchange_info():
    payload = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "status": "HALT",
                "contractType": "PERPETUAL",
                "filters": [{"filterType": "LOT_SIZE", "stepSize": "0.001"}],
            }
        ]
    }
    result = parse_usdm_exchange_info(payload)
    assert len(result) == 1
    m = result[0]
    assert m.symbol == "BTCUSDT"
    assert m.status == SymbolStatus.HALT
    assert m.market_scope == MarketScope.USDM_FUTURES
    assert m.contract_type == "PERPETUAL"
    assert SymbolFilterType.LOT_SIZE in m.filters


def test_parse_24h_tickers():
    payload = [
        {
            "symbol": "BTCUSDT",
            "priceChangePercent": "1.2",
            "lastPrice": "50000",
            "volume": "100",
            "quoteVolume": "5000000",
            "count": 1000,
        },
        {"symbol": "INVALID", "priceChangePercent": "bad"},
    ]
    result = parse_24h_tickers(payload, MarketScope.SPOT)
    assert "BTCUSDT" in result
    t = result["BTCUSDT"]
    assert t.last_price == Decimal("50000")
    assert t.trade_count == 1000


def test_parse_book_tickers():
    payload = [
        {
            "symbol": "BTCUSDT",
            "bidPrice": "50000",
            "bidQty": "1",
            "askPrice": "50010",
            "askQty": "2",
        }
    ]
    result = parse_book_tickers(payload, MarketScope.SPOT)
    assert "BTCUSDT" in result
    b = result["BTCUSDT"]
    assert b.bid_price == Decimal("50000")
    assert b.ask_qty == Decimal("2")
