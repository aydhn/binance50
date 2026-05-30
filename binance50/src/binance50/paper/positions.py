import uuid
from decimal import Decimal
from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.paper.models import PaperPosition, PaperFill, PaperOrder, PaperOrderSide
from binance50.core.exceptions import PaperPositionError

def update_position_from_fill(position: PaperPosition | None, fill: PaperFill, order: PaperOrder, config: AppConfig) -> PaperPosition:
    if position is None:
        if order.side == PaperOrderSide.sell and not config.paper_execution.ledger.allow_short_spot:
            raise PaperPositionError(f"Cannot sell without existing position (short spot forbidden): {order.symbol}")

        position = PaperPosition(
            position_id=f"pos_{uuid.uuid4().hex[:8]}",
            symbol=order.symbol,
            quantity=Decimal("0.0"),
            avg_entry_price=Decimal("0.0"),
            market_price=fill.fill_price,
            updated_at_utc=datetime.now(timezone.utc)
        )

    if order.side == PaperOrderSide.buy:
        return open_or_increase_spot_position(position, fill, config)
    else:
        return reduce_or_close_spot_position(position, fill, config)

def open_or_increase_spot_position(position: PaperPosition, fill: PaperFill, config: AppConfig) -> PaperPosition:
    new_quantity = position.quantity + fill.fill_quantity
    if new_quantity > 0:
        position.avg_entry_price = compute_average_entry_price(
            position.quantity, position.avg_entry_price,
            fill.fill_quantity, fill.fill_price
        )
    position.quantity = new_quantity
    position.total_fees_usdt += fill.fee_usdt
    position.total_slippage_usdt += fill.slippage_cost_usdt
    position.updated_at_utc = datetime.now(timezone.utc)
    return position

def reduce_or_close_spot_position(position: PaperPosition, fill: PaperFill, config: AppConfig) -> PaperPosition:
    if not config.paper_execution.ledger.allow_short_spot and fill.fill_quantity > position.quantity:
        raise PaperPositionError(f"Sell quantity ({fill.fill_quantity}) exceeds position ({position.quantity})")

    realized_pnl = (fill.fill_price - position.avg_entry_price) * fill.fill_quantity
    position.realized_pnl_usdt += realized_pnl

    position.quantity -= fill.fill_quantity
    if position.quantity == 0:
        position.avg_entry_price = Decimal("0.0")

    position.total_fees_usdt += fill.fee_usdt
    position.total_slippage_usdt += fill.slippage_cost_usdt
    position.updated_at_utc = datetime.now(timezone.utc)
    return position

def compute_average_entry_price(old_qty: Decimal, old_price: Decimal, new_qty: Decimal, new_price: Decimal) -> Decimal:
    total_qty = old_qty + new_qty
    if total_qty == 0:
        return Decimal("0.0")
    return ((old_qty * old_price) + (new_qty * new_price)) / total_qty

def validate_position(position: PaperPosition, config: AppConfig) -> None:
    if not config.paper_execution.ledger.allow_short_spot and position.quantity < 0:
        raise PaperPositionError("Short spot position detected")

def build_positions_report(positions: list[PaperPosition]) -> dict:
    return {"open_positions": len([p for p in positions if p.quantity > 0])}
