from decimal import Decimal

from binance50.core.enums import MarketScope
from binance50.universe.models import (
    BookTicker,
    SymbolDecisionStatus,
    SymbolFilter,
    SymbolFilterType,
    SymbolMetadata,
    SymbolStatus,
    Ticker24h,
    UniverseCandidate,
    UniverseSelectionResult,
)


def test_symbol_filter_parse():
    f = SymbolFilter(
        filter_type=SymbolFilterType.PRICE_FILTER,
        raw={"minPrice": "0.1", "maxPrice": "100", "tickSize": "0.1"},
        min_price=Decimal("0.1"),
        max_price=Decimal("100"),
        tick_size=Decimal("0.1"),
    )
    assert f.filter_type == SymbolFilterType.PRICE_FILTER
    assert f.min_price == Decimal("0.1")


def test_symbol_metadata_valid():
    m = SymbolMetadata(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        status=SymbolStatus.TRADING,
        market_scope=MarketScope.SPOT,
    )
    assert m.symbol == "BTCUSDT"
    assert m.status == SymbolStatus.TRADING


def test_ticker24h_decimal_fields():
    t = Ticker24h(
        symbol="BTCUSDT",
        price_change_percent=Decimal("1.5"),
        last_price=Decimal("60000"),
        volume=Decimal("10"),
        quote_volume=Decimal("600000"),
        trade_count=1000,
    )
    assert t.volume == Decimal("10")
    assert isinstance(t.last_price, Decimal)


def test_book_ticker_valid():
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("60000"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("60010"),
        ask_qty=Decimal("2"),
    )
    assert b.bid_price == Decimal("60000")


def test_universe_candidate_rejection_reasons():
    m = SymbolMetadata(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        status=SymbolStatus.TRADING,
        market_scope=MarketScope.SPOT,
    )
    c = UniverseCandidate(symbol="BTCUSDT", market_scope=MarketScope.SPOT, metadata=m)
    assert len(c.rejection_reasons) == 0
    assert c.decision_status == SymbolDecisionStatus.WARNING


def test_universe_selection_result_unique_selected_symbols():
    r = UniverseSelectionResult(selected_symbols=["BTCUSDT", "ETHUSDT"])
    assert "BTCUSDT" in r.selected_symbols
    assert len(r.selected_symbols) == 2
