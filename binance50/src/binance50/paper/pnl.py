from decimal import Decimal
from pydantic import BaseModel
import pandas as pd
from typing import Any
from binance50.config.models import AppConfig
from binance50.paper.models import PaperPosition, PaperLedgerEvent, PaperBalanceSnapshot
from binance50.core.exceptions import PaperPnLError

class PaperPnLReport(BaseModel):
    run_id: str
    starting_cash_usdt: Decimal
    ending_cash_usdt: Decimal
    ending_equity_usdt: Decimal
    realized_pnl_usdt: Decimal
    unrealized_pnl_usdt: Decimal
    total_fees_usdt: Decimal
    total_slippage_cost_usdt: Decimal
    gross_return_pct: float
    net_return_pct: float
    max_drawdown_pct: float
    win_count: int
    loss_count: int
    fill_count: int
    order_count: int
    warnings: list[str]
    metadata: dict[str, Any]

def compute_realized_pnl(fills: list, positions: list[PaperPosition], config: AppConfig) -> Decimal:
    return sum(p.realized_pnl_usdt for p in positions)

def compute_unrealized_pnl(positions: list[PaperPosition], market_prices: dict[str, Decimal], config: AppConfig) -> Decimal:
    unrealized = Decimal("0.0")
    for pos in positions:
        if pos.quantity > 0 and pos.symbol in market_prices:
            pos.market_price = market_prices[pos.symbol]
            pos.unrealized_pnl_usdt = (pos.market_price - pos.avg_entry_price) * pos.quantity
            unrealized += pos.unrealized_pnl_usdt
    return unrealized

def compute_equity_curve(ledger_events: list[PaperLedgerEvent], balance_snapshots: list[PaperBalanceSnapshot], config: AppConfig) -> pd.DataFrame:
    data = []
    for snap in balance_snapshots:
        data.append({
            "timestamp": snap.created_at_utc,
            "equity": float(snap.equity_usdt)
        })
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["timestamp", "equity"])

def compute_paper_drawdown(equity_curve: pd.DataFrame) -> float:
    if equity_curve.empty: return 0.0
    equity = equity_curve["equity"]
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    return float(drawdown.min() * 100) if not drawdown.empty and drawdown.min() < 0 else 0.0

def build_paper_pnl_report(
    run_id: str,
    starting_cash: Decimal,
    ending_cash: Decimal,
    ending_equity: Decimal,
    positions: list[PaperPosition],
    fills: list,
    orders: list,
    equity_curve: pd.DataFrame,
    config: AppConfig
) -> PaperPnLReport:
    realized = sum(p.realized_pnl_usdt for p in positions)
    unrealized = sum(p.unrealized_pnl_usdt for p in positions)
    fees = sum(p.total_fees_usdt for p in positions)
    slippage = sum(p.total_slippage_usdt for p in positions)

    net_return = 0.0
    if starting_cash > 0:
        net_return = float((ending_equity - starting_cash) / starting_cash) * 100.0

    return PaperPnLReport(
        run_id=run_id,
        starting_cash_usdt=starting_cash,
        ending_cash_usdt=ending_cash,
        ending_equity_usdt=ending_equity,
        realized_pnl_usdt=realized,
        unrealized_pnl_usdt=unrealized,
        total_fees_usdt=fees,
        total_slippage_cost_usdt=slippage,
        gross_return_pct=net_return, # simplified
        net_return_pct=net_return,
        max_drawdown_pct=compute_paper_drawdown(equity_curve),
        win_count=len([p for p in positions if p.realized_pnl_usdt > 0]),
        loss_count=len([p for p in positions if p.realized_pnl_usdt < 0]),
        fill_count=len(fills),
        order_count=len(orders),
        warnings=[],
        metadata={}
    )

def validate_pnl_report(report: PaperPnLReport, config: AppConfig) -> None:
    pass
