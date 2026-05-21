from decimal import Decimal

from binance50.universe.models import BookTicker
from binance50.universe.spread import (
    classify_spread,
    compute_spread_metrics,
    is_spread_acceptable,
    spread_score,
)


def test_spread_metrics():
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("100"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("101"),
        ask_qty=Decimal("1"),
    )

    m = compute_spread_metrics(b)
    assert m.valid
    assert m.mid == Decimal("100.5")
    assert m.spread_abs == Decimal("1")
    # bps = 1 / 100.5 * 10000 = ~99.5
    assert Decimal("99.5") <= m.spread_bps <= Decimal("99.6")


def test_spread_invalid():
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("101"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("100"),
        ask_qty=Decimal("1"),
    )
    m = compute_spread_metrics(b)
    assert not m.valid


def test_spread_acceptable():
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("10000"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("10001"),
        ask_qty=Decimal("1"),
    )
    m = compute_spread_metrics(b)
    assert is_spread_acceptable(m, max_spread_bps=10.0)
    assert not is_spread_acceptable(m, max_spread_bps=0.5)


def test_classify_spread():
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("10000"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("10005"),
        ask_qty=Decimal("1"),
    )
    m = compute_spread_metrics(b)
    # mid = 10002.5, spread_abs = 5, bps = ~5.0

    assert classify_spread(m, warning_bps=3.0, max_bps=10.0) == "warning"
    assert classify_spread(m, warning_bps=8.0, max_bps=10.0) == "acceptable"
    assert classify_spread(m, warning_bps=2.0, max_bps=4.0) == "rejected"


def test_spread_score():
    b = BookTicker(
        symbol="BTCUSDT",
        bid_price=Decimal("10000"),
        bid_qty=Decimal("1"),
        ask_price=Decimal("10005"),
        ask_qty=Decimal("1"),
    )
    m = compute_spread_metrics(b)
    # bps ~ 5.0

    # if max is 10.0, score is ~50
    score = spread_score(m, max_spread_bps=10.0)
    assert 49.0 <= score <= 51.0

    # if max is 5.0, score is ~0
    score = spread_score(m, max_spread_bps=5.0)
    assert 0.0 <= score <= 1.0
