import pandas as pd

from .models import (
    BacktestEquityPoint,
    BacktestEvent,
    BacktestFill,
    BacktestPosition,
    BacktestTrade,
)


def build_backtest_timeline(
    events: list[BacktestEvent],
    fills: list[BacktestFill],
    positions: list[BacktestPosition],
    trades: list[BacktestTrade],
    equity_curve: list[BacktestEquityPoint],
) -> pd.DataFrame:
    # Stub
    return pd.DataFrame()


def validate_timeline_order(timeline: pd.DataFrame) -> None:
    pass


def explain_timeline_row(row: pd.Series) -> dict:
    return {}
