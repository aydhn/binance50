import uuid

from .models import BacktestFill, BacktestPosition, BacktestPositionStatus


class BacktestPositionManager:
    def open_from_fill(
        self, fill: BacktestFill, source_signal_id: str, source_risk_id: str
    ) -> BacktestPosition:
        return BacktestPosition(
            position_id=str(uuid.uuid4()),
            run_id=fill.run_id,
            symbol=fill.symbol,
            side=fill.side,
            status=BacktestPositionStatus.open,
            opened_at=fill.fill_time,
            open_price=fill.simulated_price,
            simulated_quantity=fill.simulated_quantity,
            simulated_notional_usdt=fill.simulated_notional_usdt,
            fees_paid_usdt=fill.simulated_fee_usdt,
            slippage_paid_usdt=fill.simulated_notional_usdt
            * (fill.simulated_slippage_bps / 10000.0),
            source_signal_id=source_signal_id,
            source_risk_assessment_id=source_risk_id,
        )

    def close_from_fill(
        self, position: BacktestPosition, fill: BacktestFill, reason: str
    ) -> BacktestPosition:
        position.status = BacktestPositionStatus.closed
        position.closed_at = fill.fill_time
        position.close_price = fill.simulated_price
        position.close_reason = reason
        position.fees_paid_usdt += fill.simulated_fee_usdt
        position.slippage_paid_usdt += fill.simulated_notional_usdt * (
            fill.simulated_slippage_bps / 10000.0
        )
        return position

    def mark_to_market(
        self, open_positions: list[BacktestPosition], price_map: dict
    ) -> list[BacktestPosition]:
        for p in open_positions:
            if p.symbol in price_map:
                current_price = price_map[p.symbol]
                if p.side == "buy":
                    p.unrealized_pnl_usdt = (current_price - p.open_price) * p.simulated_quantity
                else:
                    p.unrealized_pnl_usdt = (p.open_price - current_price) * p.simulated_quantity
        return open_positions

    def close_positions_on_opposite_signal(self, open_positions, signals):
        pass

    def close_positions_on_max_holding_bars(self, open_positions, current_bar):
        pass

    def close_all_at_end(self, last_bar):
        pass

    def validate_positions(self):
        pass
