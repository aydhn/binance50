
from pydantic import BaseModel

from .models import BacktestEquityPoint, BacktestPosition, BacktestTrade


class BacktestMetrics(BaseModel):
    run_id: str
    start_equity_usdt: float
    end_equity_usdt: float
    total_return_pct: float
    max_drawdown_pct: float
    trade_count: int
    win_count: int
    loss_count: int
    win_rate_pct: float
    gross_profit_usdt: float
    gross_loss_usdt: float
    profit_factor: float
    expectancy_usdt: float
    avg_win_usdt: float
    avg_loss_usdt: float
    avg_trade_usdt: float
    median_trade_usdt: float
    exposure_time_pct: float
    turnover_usdt: float
    total_fees_usdt: float
    total_slippage_usdt: float
    fee_impact_pct: float
    slippage_impact_pct: float
    annualized_return_placeholder: float = 0.0
    sharpe_placeholder: float = 0.0
    sortino_placeholder: float = 0.0
    warnings: list[str] = []

def compute_backtest_metrics(trades: list[BacktestTrade], equity_curve: list[BacktestEquityPoint], positions: list[BacktestPosition], config) -> BacktestMetrics:
    # Stub implementation
    return BacktestMetrics(
        run_id="run_id",
        start_equity_usdt=1000.0,
        end_equity_usdt=1000.0,
        total_return_pct=0.0,
        max_drawdown_pct=0.0,
        trade_count=len(trades),
        win_count=0,
        loss_count=0,
        win_rate_pct=0.0,
        gross_profit_usdt=0.0,
        gross_loss_usdt=0.0,
        profit_factor=0.0,
        expectancy_usdt=0.0,
        avg_win_usdt=0.0,
        avg_loss_usdt=0.0,
        avg_trade_usdt=0.0,
        median_trade_usdt=0.0,
        exposure_time_pct=0.0,
        turnover_usdt=0.0,
        total_fees_usdt=0.0,
        total_slippage_usdt=0.0,
        fee_impact_pct=0.0,
        slippage_impact_pct=0.0
    )

def compute_win_rate(trades: list[BacktestTrade]) -> float:
    return 0.0

def compute_profit_factor(trades: list[BacktestTrade]) -> float:
    return 0.0

def compute_expectancy(trades: list[BacktestTrade]) -> float:
    return 0.0

def compute_exposure_time(equity_curve: list[BacktestEquityPoint]) -> float:
    return 0.0

def compute_turnover(trades: list[BacktestTrade]) -> float:
    return 0.0

def compute_fee_impact(trades: list[BacktestTrade], equity_curve: list[BacktestEquityPoint]) -> float:
    return 0.0

def compute_slippage_impact(trades: list[BacktestTrade], equity_curve: list[BacktestEquityPoint]) -> float:
    return 0.0

def validate_metrics(metrics: BacktestMetrics, config) -> None:
    pass
