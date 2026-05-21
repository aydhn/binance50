from decimal import Decimal

from binance50.universe.models import BookTicker, SpreadMetrics


def compute_spread_metrics(book: BookTicker) -> SpreadMetrics:
    bid = book.bid_price
    ask = book.ask_price

    if bid <= Decimal("0") or ask <= Decimal("0") or ask < bid:
        return SpreadMetrics(
            symbol=book.symbol,
            bid=bid,
            ask=ask,
            mid=Decimal("0"),
            spread_abs=Decimal("0"),
            spread_bps=Decimal("0"),
            valid=False,
        )

    mid = (bid + ask) / Decimal("2")
    if mid <= Decimal("0"):
        return SpreadMetrics(
            symbol=book.symbol,
            bid=bid,
            ask=ask,
            mid=Decimal("0"),
            spread_abs=Decimal("0"),
            spread_bps=Decimal("0"),
            valid=False,
        )

    spread_abs = ask - bid
    spread_bps = (spread_abs / mid) * Decimal("10000")

    return SpreadMetrics(
        symbol=book.symbol,
        bid=bid,
        ask=ask,
        mid=mid,
        spread_abs=spread_abs,
        spread_bps=spread_bps,
        valid=True,
    )


def is_spread_acceptable(metrics: SpreadMetrics, max_spread_bps: float) -> bool:
    if not metrics.valid:
        return False
    return metrics.spread_bps <= Decimal(str(max_spread_bps))


def classify_spread(metrics: SpreadMetrics, warning_bps: float, max_bps: float) -> str:
    if not metrics.valid:
        return "invalid"
    if metrics.spread_bps > Decimal(str(max_bps)):
        return "rejected"
    if metrics.spread_bps > Decimal(str(warning_bps)):
        return "warning"
    return "acceptable"


def spread_score(metrics: SpreadMetrics, max_spread_bps: float) -> float:
    if not metrics.valid or metrics.spread_bps > Decimal(str(max_spread_bps)):
        return 0.0

    # Simple linear scoring: 0 bps = 100 score, max_bps = 0 score
    ratio = float(metrics.spread_bps) / max_spread_bps
    score = 100.0 * (1.0 - ratio)
    return max(0.0, min(100.0, score))
