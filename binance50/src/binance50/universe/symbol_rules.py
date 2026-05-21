from decimal import Decimal

from binance50.config.models import UniverseConfig
from binance50.universe.models import (
    SymbolFilter,
    SymbolFilterType,
    SymbolMetadata,
    SymbolRejectionReason,
    SymbolRuleQuality,
    Ticker24h,
)


def extract_price_filter(metadata: SymbolMetadata) -> SymbolFilter | None:
    return metadata.filters.get(SymbolFilterType.PRICE_FILTER)


def extract_lot_size_filter(metadata: SymbolMetadata) -> SymbolFilter | None:
    return metadata.filters.get(SymbolFilterType.LOT_SIZE)


def extract_min_notional_filter(metadata: SymbolMetadata) -> SymbolFilter | None:
    return metadata.filters.get(SymbolFilterType.MIN_NOTIONAL)


def extract_notional_filter(metadata: SymbolMetadata) -> SymbolFilter | None:
    return metadata.filters.get(SymbolFilterType.NOTIONAL)


def compute_price_tick_pct(last_price: Decimal, tick_size: Decimal) -> Decimal | None:
    if last_price <= Decimal("0") or tick_size <= Decimal("0"):
        return None
    return (tick_size / last_price) * Decimal("100")


def compute_qty_step_pct(reference_qty: Decimal, step_size: Decimal) -> Decimal | None:
    if reference_qty <= Decimal("0") or step_size <= Decimal("0"):
        return None
    return (step_size / reference_qty) * Decimal("100")


def evaluate_symbol_rule_quality(
    metadata: SymbolMetadata, ticker: Ticker24h, config: UniverseConfig
) -> SymbolRuleQuality:
    price_filter = extract_price_filter(metadata)
    lot_size = extract_lot_size_filter(metadata)
    min_notional_filter = extract_min_notional_filter(metadata)
    notional_filter = extract_notional_filter(metadata)

    # notional is newer variant of min_notional in some endpoints
    actual_min_notional = None
    if min_notional_filter and min_notional_filter.min_notional is not None:
        actual_min_notional = min_notional_filter.min_notional
    elif notional_filter and notional_filter.min_notional is not None:
        actual_min_notional = notional_filter.min_notional

    tick_size = price_filter.tick_size if price_filter else None
    step_size = lot_size.step_size if lot_size else None

    price_tick_pct = None
    if tick_size is not None and ticker.last_price > Decimal("0"):
        price_tick_pct = compute_price_tick_pct(ticker.last_price, tick_size)

    qty_step_pct = None
    if step_size is not None and ticker.last_price > Decimal("0"):
        # Assume a reference order of 100 USDT equivalent to test step size roughness
        reference_qty = Decimal("100") / ticker.last_price
        qty_step_pct = compute_qty_step_pct(reference_qty, step_size)

    warnings = []
    score = 100.0

    if not price_filter:
        warnings.append("Missing PRICE_FILTER")
        score -= 40
    if not lot_size:
        warnings.append("Missing LOT_SIZE filter")
        score -= 40
    if actual_min_notional is None:
        warnings.append("Missing MIN_NOTIONAL or NOTIONAL filter")
        score -= 20

    if price_tick_pct is not None and price_tick_pct > Decimal(str(config.max_price_tick_pct)):
        warnings.append(f"Price tick pct {price_tick_pct:.4f}% > max {config.max_price_tick_pct}%")
        score -= 30

    if qty_step_pct is not None and qty_step_pct > Decimal(str(config.max_qty_step_pct)):
        warnings.append(f"Qty step pct {qty_step_pct:.4f}% > max {config.max_qty_step_pct}%")
        score -= 30

    return SymbolRuleQuality(
        symbol=metadata.symbol,
        has_price_filter=price_filter is not None,
        has_lot_size=lot_size is not None,
        has_min_notional=actual_min_notional is not None,
        min_notional=actual_min_notional,
        tick_size=tick_size,
        step_size=step_size,
        price_tick_pct=price_tick_pct,
        qty_step_pct=qty_step_pct,
        quality_score=max(0.0, score),
        warnings=warnings,
    )


def validate_symbol_order_filters(
    metadata: SymbolMetadata, config: UniverseConfig
) -> list[SymbolRejectionReason]:
    reasons = []

    price_filter = extract_price_filter(metadata)
    lot_size = extract_lot_size_filter(metadata)
    min_notional_filter = extract_min_notional_filter(metadata)
    notional_filter = extract_notional_filter(metadata)

    actual_min_notional = None
    if min_notional_filter and min_notional_filter.min_notional is not None:
        actual_min_notional = min_notional_filter.min_notional
    elif notional_filter and notional_filter.min_notional is not None:
        actual_min_notional = notional_filter.min_notional

    if config.require_filters and (not price_filter or not lot_size or actual_min_notional is None):
        reasons.append(SymbolRejectionReason.MISSING_FILTERS)

    if actual_min_notional is not None and actual_min_notional > Decimal(
        str(config.min_notional_ceiling_usdt)
    ):
        reasons.append(SymbolRejectionReason.MIN_NOTIONAL_TOO_HIGH)

    return reasons
