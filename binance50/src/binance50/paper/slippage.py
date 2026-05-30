from decimal import Decimal
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderSide, PaperFill

def compute_slippage_bps(order: PaperOrder, bar: dict, config: AppConfig) -> Decimal:
    if not config.paper_execution.slippage.enabled:
        return Decimal("0.0")
    # basic simulated slippage
    return config.paper_execution.slippage.default_slippage_bps

def apply_slippage_to_fill_price(order: PaperOrder, raw_price: Decimal, slippage_bps: Decimal, config: AppConfig) -> Decimal:
    if slippage_bps == 0:
        return raw_price

    slippage_factor = slippage_bps / Decimal("10000.0")
    if order.side == PaperOrderSide.buy:
        return raw_price * (Decimal("1.0") + slippage_factor)
    else:
        return raw_price * (Decimal("1.0") - slippage_factor)

def compute_slippage_cost_usdt(order: PaperOrder, raw_price: Decimal, slipped_price: Decimal, quantity: Decimal) -> Decimal:
    if order.side == PaperOrderSide.buy:
        return (slipped_price - raw_price) * quantity
    else:
        return (raw_price - slipped_price) * quantity

def build_slippage_report(fills: list[PaperFill], config: AppConfig) -> dict:
    total_slippage = sum(f.slippage_cost_usdt for f in fills)
    return {"total_slippage_cost_usdt": str(total_slippage), "fill_count": len(fills)}
