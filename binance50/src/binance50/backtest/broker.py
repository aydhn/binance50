import uuid

from .models import BacktestFill, BacktestPosition, BacktestPositionStatus


class BacktestSimulatedBroker:
    def __init__(self, config):
        self.config = config
        self.cash_usdt = 0.0
        self._open_positions: dict[str, BacktestPosition] = {}
        self._closed_positions: list[BacktestPosition] = []

    def initialize_cash(self, starting_cash_usdt: float):
        self.cash_usdt = starting_cash_usdt

    def can_open_position(self, symbol: str, notional_usdt: float) -> bool:
        if symbol in self._open_positions:
            return False
        if notional_usdt > self.cash_usdt * (
            self.config.backtest.capital.max_cash_usage_pct / 100.0
        ):
            return False
        if len(self._open_positions) >= self.config.backtest.capital.max_open_positions:
            return False
        return True

    def open_position(self, fill: BacktestFill, context: dict) -> BacktestPosition:
        position = BacktestPosition(
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
            source_risk_assessment_id=fill.source_risk_assessment_id,
        )
        self._open_positions[fill.symbol] = position
        self.update_cash_for_open(fill)
        return position

    def close_position(self, position_id: str, fill: BacktestFill, reason: str) -> BacktestPosition:
        position = next(
            (p for p in self._open_positions.values() if p.position_id == position_id), None
        )
        if not position:
            raise ValueError(f"Position {position_id} not found")
        position.status = BacktestPositionStatus.closed
        position.closed_at = fill.fill_time
        position.close_price = fill.simulated_price
        position.close_reason = reason
        position.fees_paid_usdt += fill.simulated_fee_usdt
        position.slippage_paid_usdt += fill.simulated_notional_usdt * (
            fill.simulated_slippage_bps / 10000.0
        )

        # Calculate PnL
        if position.side == "buy":
            position.realized_pnl_usdt = (
                fill.simulated_price - position.open_price
            ) * position.simulated_quantity
        else:
            position.realized_pnl_usdt = (
                position.open_price - fill.simulated_price
            ) * position.simulated_quantity

        if self.config.backtest.fees.include_fees_in_pnl:
            position.realized_pnl_usdt -= position.fees_paid_usdt
        if self.config.backtest.slippage.include_slippage_in_pnl:
            position.realized_pnl_usdt -= position.slippage_paid_usdt

        del self._open_positions[fill.symbol]
        self._closed_positions.append(position)
        self.update_cash_for_close(position)
        return position

    def get_open_position(self, symbol: str) -> BacktestPosition | None:
        return self._open_positions.get(symbol)

    def list_open_positions(self) -> list[BacktestPosition]:
        return list(self._open_positions.values())

    def list_closed_positions(self) -> list[BacktestPosition]:
        return list(self._closed_positions)

    def update_cash_for_open(self, fill: BacktestFill):
        self.cash_usdt -= fill.simulated_notional_usdt
        self.cash_usdt -= fill.simulated_fee_usdt
        self.cash_usdt -= fill.simulated_notional_usdt * (fill.simulated_slippage_bps / 10000.0)

    def update_cash_for_close(self, position: BacktestPosition):
        self.cash_usdt += position.simulated_notional_usdt + position.realized_pnl_usdt

    def validate_state(self):
        if not self.config.backtest.capital.allow_negative_cash and self.cash_usdt < 0:
            raise ValueError("Negative cash is not allowed")
