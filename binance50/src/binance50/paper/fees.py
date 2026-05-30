from decimal import Decimal
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderType, PaperFill

def compute_paper_fee_usdt(order: PaperOrder, fill: PaperFill, config: AppConfig) -> Decimal:
    if not config.paper_execution.fees.enabled:
        return Decimal("0.0")

    fee_rate_bps = choose_fee_rate_bps(order, config)
    fee_usdt = fill.gross_amount_usdt * (fee_rate_bps / Decimal("10000.0"))
    return fee_usdt

def choose_fee_rate_bps(order: PaperOrder, config: AppConfig) -> Decimal:
    if order.order_type == PaperOrderType.market:
        return config.paper_execution.fees.taker_fee_bps
    return config.paper_execution.fees.maker_fee_bps

def apply_fee_to_fill(fill: PaperFill, fee_usdt: Decimal) -> PaperFill:
    fill.fee_usdt = fee_usdt
    return fill

def build_fee_report(fills: list[PaperFill], config: AppConfig) -> dict:
    total_fee = sum(f.fee_usdt for f in fills)
    return {"total_fee_usdt": str(total_fee), "fill_count": len(fills)}
