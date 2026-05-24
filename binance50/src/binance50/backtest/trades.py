import uuid

import pandas as pd

from .models import BacktestPosition, BacktestTrade


def build_trade_from_closed_position(position: BacktestPosition, context: dict) -> BacktestTrade:
    if position.close_price is None or position.closed_at is None:
        raise ValueError("Position must be closed to build a trade")

    return BacktestTrade(
        trade_id=str(uuid.uuid4()),
        run_id=position.run_id,
        position_id=position.position_id,
        symbol=position.symbol,
        interval=context.get("interval", "UNKNOWN"),
        opened_at=position.opened_at,
        closed_at=position.closed_at,
        side=position.side,
        entry_price=position.open_price,
        exit_price=position.close_price,
        simulated_quantity=position.simulated_quantity,
        gross_pnl_usdt=position.realized_pnl_usdt + position.fees_paid_usdt + position.slippage_paid_usdt,
        net_pnl_usdt=position.realized_pnl_usdt,
        return_pct=position.realized_pnl_usdt / position.simulated_notional_usdt if position.simulated_notional_usdt > 0 else 0,
        fees_usdt=position.fees_paid_usdt,
        slippage_cost_usdt=position.slippage_paid_usdt,
        holding_bars=position.holding_bars,
        close_reason=position.close_reason or "UNKNOWN",
        explanation="Simulated backtest trade"
    )

def trades_to_dataframe(trades: list[BacktestTrade]) -> pd.DataFrame:
    if not trades:
        return pd.DataFrame()
    return pd.DataFrame([t.model_dump() for t in trades])

def dataframe_to_trades(df: pd.DataFrame) -> list[BacktestTrade]:
    return [BacktestTrade(**row) for row in df.to_dict('records')]

def validate_trade(trade: BacktestTrade, config) -> None:
    pass

def summarize_trades(trades: list[BacktestTrade]) -> dict:
    if not trades:
        return {}
    df = trades_to_dataframe(trades)
    return {
        "count": len(df),
        "total_net_pnl": df['net_pnl_usdt'].sum(),
        "win_rate": len(df[df['net_pnl_usdt'] > 0]) / len(df) if len(df) > 0 else 0
    }
