from decimal import Decimal

from binance50.config.models import UniverseConfig
from binance50.universe.liquidity import (
    compute_liquidity_metrics,
    is_liquidity_acceptable,
    liquidity_score,
)
from binance50.universe.models import BookTicker, Ticker24h


def test_liquidity_metrics():
    t = Ticker24h(
        symbol="BTCUSDT",
        price_change_percent=Decimal("0"),
        last_price=Decimal("50000"),
        volume=Decimal("100"),
        quote_volume=Decimal("5000000"),
        trade_count=1000,
    )
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("50000"),
        bid_qty=Decimal("2"),
        ask_price=Decimal("50010"),
        ask_qty=Decimal("3"),
    )

    m = compute_liquidity_metrics(t, b)
    assert m.valid
    assert m.quote_volume_24h == Decimal("5000000")
    assert m.bid_notional == Decimal("100000")
    assert m.ask_notional == Decimal("150030")
    assert m.depth_notional == Decimal("100000")


def test_liquidity_acceptable():
    c = UniverseConfig()
    c.min_quote_volume_24h_usdt = 1000.0
    c.min_trade_count_24h = 100

    t = Ticker24h(
        symbol="BTCUSDT",
        price_change_percent=Decimal("0"),
        last_price=Decimal("50000"),
        volume=Decimal("100"),
        quote_volume=Decimal("5000"),
        trade_count=500,
    )
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("50000"),
        bid_qty=Decimal("2"),
        ask_price=Decimal("50010"),
        ask_qty=Decimal("3"),
    )

    m = compute_liquidity_metrics(t, b)
    assert is_liquidity_acceptable(m, c)

    t.quote_volume = Decimal("500")
    m = compute_liquidity_metrics(t, b)
    assert not is_liquidity_acceptable(m, c)

    t.quote_volume = Decimal("5000")
    t.trade_count = 50
    m = compute_liquidity_metrics(t, b)
    assert not is_liquidity_acceptable(m, c)


def test_liquidity_score():
    c = UniverseConfig()
    c.min_quote_volume_24h_usdt = 1000.0

    t = Ticker24h(
        symbol="BTCUSDT",
        price_change_percent=Decimal("0"),
        last_price=Decimal("50000"),
        volume=Decimal("100"),
        quote_volume=Decimal("10000"),  # 10x min
        trade_count=10000,
    )
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("50000"),
        bid_qty=Decimal("2"),
        ask_price=Decimal("50010"),
        ask_qty=Decimal("3"),
    )

    m = compute_liquidity_metrics(t, b)
    score = liquidity_score(m, c)
    assert score == 100.0

    t.quote_volume = Decimal("5500")  # 5.5x min (4.5 above min) -> 4.5/9 = 0.5 -> 50 score
    m = compute_liquidity_metrics(t, b)
    score = liquidity_score(m, c)
    assert score == 50.0
