from .models import BacktestEquityPoint, BacktestPosition


class BacktestPortfolio:
    def __init__(self, run_id: str, starting_cash_usdt: float):
        self.run_id = run_id
        self.cash_usdt = starting_cash_usdt
        self.equity_usdt = starting_cash_usdt
        self.unrealized_pnl_usdt = 0.0
        self.realized_pnl_usdt = 0.0
        self.open_position_count = 0

    def update_after_open(self, position: BacktestPosition, fill):
        self.cash_usdt -= fill.simulated_notional_usdt
        self.cash_usdt -= fill.simulated_fee_usdt
        self.cash_usdt -= fill.simulated_notional_usdt * (fill.simulated_slippage_bps / 10000.0)
        self.open_position_count += 1

    def update_after_close(self, position: BacktestPosition, fill):
        self.cash_usdt += position.simulated_notional_usdt + position.realized_pnl_usdt
        self.realized_pnl_usdt += position.realized_pnl_usdt
        self.open_position_count -= 1

    def mark_to_market(self, open_positions: list[BacktestPosition], current_bar: dict):
        self.unrealized_pnl_usdt = sum(p.unrealized_pnl_usdt for p in open_positions)
        self.compute_cash_equity()

    def compute_cash_equity(self):
        self.equity_usdt = self.cash_usdt + self.unrealized_pnl_usdt

    def snapshot(self, open_time: int) -> BacktestEquityPoint:
        return BacktestEquityPoint(
            run_id=self.run_id,
            open_time=open_time,
            cash_usdt=self.cash_usdt,
            equity_usdt=self.equity_usdt,
            unrealized_pnl_usdt=self.unrealized_pnl_usdt,
            realized_pnl_usdt=self.realized_pnl_usdt,
            drawdown_pct=0.0,  # Computed later
            open_position_count=self.open_position_count,
        )

    def validate_portfolio(self):
        if self.cash_usdt < 0:
            raise ValueError("Negative cash in portfolio")
