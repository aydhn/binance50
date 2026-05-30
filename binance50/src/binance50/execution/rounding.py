import math
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from typing import Any, Optional

from binance50.config.models import AppConfig
from .filters import BinanceSymbolFilterSnapshot


@dataclass
class ExecutionRoundingReport:
    symbol: str
    original_price: Optional[Decimal]
    rounded_price: Optional[Decimal]
    original_quantity: Optional[Decimal]
    rounded_quantity: Optional[Decimal]
    tick_size: Optional[Decimal]
    step_size: Optional[Decimal]
    rounding_mode: str
    rounding_applied: bool
    warnings: list[str]
    metadata: dict[str, Any]


def floor_to_tick(price: Decimal, tick_size: Decimal) -> Decimal:
    """Floor a price to the nearest tick size multiplier."""
    ticks = math.floor(price / tick_size)
    return ticks * tick_size


def floor_to_step(quantity: Decimal, step_size: Decimal) -> Decimal:
    """Floor a quantity to the nearest step size multiplier."""
    steps = math.floor(quantity / step_size)
    return steps * step_size


def normalize_price_for_filter(price: Optional[Decimal], snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> Optional[Decimal]:
    if price is None:
        return None
    tick = snapshot.price_filter.get("tickSize")
    if not tick:
        return price

    rmode = config.execution.binance_filters.price_tick_rounding
    if rmode == "floor_to_tick":
        return floor_to_tick(price, tick)
    else:
        # Default fallback
        return price


def normalize_quantity_for_filter(quantity: Optional[Decimal], snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> Optional[Decimal]:
    if quantity is None:
        return None
    step = snapshot.lot_size.get("stepSize")
    if not step:
        return quantity

    rmode = config.execution.binance_filters.quantity_step_rounding
    if rmode == "floor_to_step":
        return floor_to_step(quantity, step)
    else:
        return quantity


def build_rounding_report(intent: Any, snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> ExecutionRoundingReport:
    oprice = getattr(intent, 'price', None)
    oqty = getattr(intent, 'quantity', None)

    rprice = normalize_price_for_filter(oprice, snapshot, config) if oprice else None
    rqty = normalize_quantity_for_filter(oqty, snapshot, config) if oqty else None

    applied = (oprice != rprice) or (oqty != rqty)

    warnings = []
    if oprice is None or oqty is None:
        warnings.append("not_applicable_sandbox")

    return ExecutionRoundingReport(
        symbol=getattr(intent, 'symbol', 'UNKNOWN'),
        original_price=oprice,
        rounded_price=rprice,
        original_quantity=oqty,
        rounded_quantity=rqty,
        tick_size=snapshot.price_filter.get("tickSize"),
        step_size=snapshot.lot_size.get("stepSize"),
        rounding_mode=config.execution.binance_filters.rounding_mode,
        rounding_applied=applied,
        warnings=warnings,
        metadata={}
    )
