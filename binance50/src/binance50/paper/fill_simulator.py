import uuid
from datetime import datetime, timezone
from decimal import Decimal
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderType, PaperOrderSide, PaperFill, PaperFillStatus, PaperOrderStatus
from binance50.paper.lifecycle import transition_paper_order
from binance50.core.exceptions import PaperFillSimulationError

class PaperFillSimulator:
    def simulate_fill(self, order: PaperOrder, market_data: list[dict], config: AppConfig) -> list[PaperFill]:
        if not market_data:
            raise PaperFillSimulationError("No market data provided for fill simulation")

        if config.paper_execution.fills.same_bar_fill_forbidden:
            market_data = [d for d in market_data if d.get('open_time') != order.created_open_time]

        if not market_data and config.paper_execution.fills.reject_if_no_next_bar:
            transition_paper_order(order, PaperOrderStatus.paper_expired_local, config)
            return []

        if order.order_type == PaperOrderType.market:
            if not market_data: return []
            fill = self.simulate_market_order_fill(order, market_data[0], config)
            return [fill] if fill else []
        elif order.order_type == PaperOrderType.limit:
            return self.simulate_limit_order_fill(order, market_data, config)

        return []

    def simulate_market_order_fill(self, order: PaperOrder, next_bar: dict, config: AppConfig) -> PaperFill | None:
        if config.paper_execution.fills.market_order_fill_price == "next_bar_open":
            fill_price = Decimal(str(next_bar['open']))
        else:
            fill_price = Decimal(str(next_bar['close']))

        fill = PaperFill(
            paper_fill_id=f"fill_{uuid.uuid4().hex[:8]}",
            paper_order_id=order.paper_order_id,
            symbol=order.symbol,
            side=order.side,
            fill_status=PaperFillStatus.full_fill,
            fill_open_time=next_bar['open_time'],
            fill_price=fill_price,
            fill_quantity=order.requested_quantity,
            gross_amount_usdt=fill_price * order.requested_quantity,
            fee_usdt=Decimal("0.0"),
            slippage_bps=Decimal("0.0"),
            slippage_cost_usdt=Decimal("0.0"),
            liquidity_fraction=Decimal("1.0")
        )
        self.validate_fill(fill, config)
        order.filled_quantity = order.requested_quantity
        order.avg_fill_price = fill_price
        transition_paper_order(order, PaperOrderStatus.paper_filled_local, config)
        return fill

    def simulate_limit_order_fill(self, order: PaperOrder, future_bars: list[dict], config: AppConfig) -> list[PaperFill]:
        fills = []
        for bar in future_bars:
            if order.filled_quantity >= order.requested_quantity:
                break

            low = Decimal(str(bar['low']))
            high = Decimal(str(bar['high']))

            should_fill = False
            if order.side == PaperOrderSide.buy and low <= order.limit_price:
                should_fill = True
            elif order.side == PaperOrderSide.sell and high >= order.limit_price:
                should_fill = True

            if should_fill:
                # Basic fill simulator, just full fill for now
                fill = PaperFill(
                    paper_fill_id=f"fill_{uuid.uuid4().hex[:8]}",
                    paper_order_id=order.paper_order_id,
                    symbol=order.symbol,
                    side=order.side,
                    fill_status=PaperFillStatus.full_fill,
                    fill_open_time=bar['open_time'],
                    fill_price=order.limit_price,
                    fill_quantity=order.requested_quantity - order.filled_quantity,
                    gross_amount_usdt=order.limit_price * (order.requested_quantity - order.filled_quantity),
                    fee_usdt=Decimal("0.0"),
                    slippage_bps=Decimal("0.0"),
                    slippage_cost_usdt=Decimal("0.0"),
                    liquidity_fraction=Decimal("1.0")
                )
                self.validate_fill(fill, config)
                fills.append(fill)
                order.filled_quantity += fill.fill_quantity
                order.avg_fill_price = order.limit_price
                transition_paper_order(order, PaperOrderStatus.paper_filled_local, config)
                break

        if order.filled_quantity == 0 and len(future_bars) >= config.paper_execution.fills.expire_unfilled_after_bars:
            self.expire_unfilled_order(order, config)

        return fills

    def simulate_partial_fill(self, order: PaperOrder, bar: dict, config: AppConfig) -> PaperFill:
        # Skeleton for future partial fills
        pass

    def expire_unfilled_order(self, order: PaperOrder, config: AppConfig) -> PaperOrder:
        transition_paper_order(order, PaperOrderStatus.paper_expired_local, config)
        return order

    def validate_fill(self, fill: PaperFill, config: AppConfig) -> None:
        if fill.fill_price <= 0 or fill.fill_quantity <= 0:
            raise PaperFillSimulationError("Fill price and quantity must be positive")
