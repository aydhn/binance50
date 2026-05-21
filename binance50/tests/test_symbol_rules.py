from decimal import Decimal

from binance50.config.models import UniverseConfig
from binance50.core.enums import MarketScope
from binance50.universe.models import (
    SymbolFilter,
    SymbolFilterType,
    SymbolMetadata,
    SymbolStatus,
    Ticker24h,
)
from binance50.universe.symbol_rules import (
    compute_price_tick_pct,
    compute_qty_step_pct,
    evaluate_symbol_rule_quality,
    extract_lot_size_filter,
    extract_min_notional_filter,
    extract_price_filter,
)


def get_mock_metadata() -> SymbolMetadata:
    return SymbolMetadata(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        status=SymbolStatus.TRADING,
        market_scope=MarketScope.SPOT,
        filters={
            SymbolFilterType.PRICE_FILTER: SymbolFilter(
                filter_type=SymbolFilterType.PRICE_FILTER, raw={}, tick_size=Decimal("0.01")
            ),
            SymbolFilterType.LOT_SIZE: SymbolFilter(
                filter_type=SymbolFilterType.LOT_SIZE, raw={}, step_size=Decimal("0.00001")
            ),
            SymbolFilterType.MIN_NOTIONAL: SymbolFilter(
                filter_type=SymbolFilterType.MIN_NOTIONAL, raw={}, min_notional=Decimal("10.0")
            ),
        },
    )


def test_extract_filters():
    m = get_mock_metadata()
    pf = extract_price_filter(m)
    assert pf is not None
    assert pf.tick_size == Decimal("0.01")

    ls = extract_lot_size_filter(m)
    assert ls is not None
    assert ls.step_size == Decimal("0.00001")

    mn = extract_min_notional_filter(m)
    assert mn is not None
    assert mn.min_notional == Decimal("10.0")


def test_compute_pcts():
    # 0.01 / 100 = 0.0001 -> 0.01%
    assert compute_price_tick_pct(Decimal("100"), Decimal("0.01")) == Decimal("0.01")
    assert compute_price_tick_pct(Decimal("100"), Decimal("0")) is None

    assert compute_qty_step_pct(Decimal("10"), Decimal("0.1")) == Decimal("1.0")


def test_evaluate_rule_quality():
    m = get_mock_metadata()
    t = Ticker24h(
        symbol="BTCUSDT",
        price_change_percent=Decimal("0"),
        last_price=Decimal("50000"),
        volume=Decimal("0"),
        quote_volume=Decimal("0"),
        trade_count=0,
    )
    c = UniverseConfig()

    q = evaluate_symbol_rule_quality(m, t, c)
    assert q.has_price_filter
    assert q.has_lot_size
    assert q.has_min_notional
    assert q.quality_score == 100.0
    assert len(q.warnings) == 0


def test_missing_filters_rule_quality():
    m = SymbolMetadata(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        status=SymbolStatus.TRADING,
        market_scope=MarketScope.SPOT,
    )
    t = Ticker24h(
        symbol="BTCUSDT",
        price_change_percent=Decimal("0"),
        last_price=Decimal("50000"),
        volume=Decimal("0"),
        quote_volume=Decimal("0"),
        trade_count=0,
    )
    c = UniverseConfig()

    q = evaluate_symbol_rule_quality(m, t, c)
    assert not q.has_price_filter
    assert not q.has_lot_size
    assert not q.has_min_notional
    assert q.quality_score == 0.0
    assert len(q.warnings) == 3
