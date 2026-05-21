from decimal import Decimal

from binance50.config.models import UniverseConfig
from binance50.universe.models import BookTicker, LiquidityMetrics, Ticker24h


def compute_liquidity_metrics(ticker: Ticker24h, book: BookTicker) -> LiquidityMetrics:
    bid_notional = book.bid_price * book.bid_qty
    ask_notional = book.ask_price * book.ask_qty
    depth_notional = min(bid_notional, ask_notional)

    valid = True
    if ticker.quote_volume <= Decimal("0") or ticker.trade_count <= 0:
        valid = False

    return LiquidityMetrics(
        symbol=ticker.symbol,
        quote_volume_24h=ticker.quote_volume,
        base_volume_24h=ticker.volume,
        trade_count_24h=ticker.trade_count,
        bid_notional=bid_notional,
        ask_notional=ask_notional,
        depth_notional=depth_notional,
        valid=valid,
    )


def is_liquidity_acceptable(metrics: LiquidityMetrics, config: UniverseConfig) -> bool:
    if not metrics.valid:
        return False

    if metrics.quote_volume_24h < Decimal(str(config.min_quote_volume_24h_usdt)):
        return False

    if metrics.trade_count_24h < config.min_trade_count_24h:
        return False

    return True


def classify_liquidity(metrics: LiquidityMetrics, config: UniverseConfig) -> str:
    if not metrics.valid:
        return "invalid"

    if not is_liquidity_acceptable(metrics, config):
        return "rejected"

    if metrics.depth_notional < Decimal(str(config.min_bid_ask_qty_notional_usdt)):
        return "warning"

    return "acceptable"


def liquidity_score(metrics: LiquidityMetrics, config: UniverseConfig) -> float:
    if not is_liquidity_acceptable(metrics, config):
        return 0.0

    # Scale based on quote volume relative to min required, cap at a reasonable multiple
    # e.g., 10x the minimum gives a perfect score of 100
    min_vol = float(config.min_quote_volume_24h_usdt)
    if min_vol <= 0:
        return 100.0

    vol = float(metrics.quote_volume_24h)
    ratio = (vol - min_vol) / (min_vol * 9.0)  # 9x more to get from 0 to 100

    score = ratio * 100.0
    return max(0.0, min(100.0, score))
