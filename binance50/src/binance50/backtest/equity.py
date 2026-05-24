
import pandas as pd

from .models import BacktestEquityPoint


def build_equity_curve(points: list[BacktestEquityPoint]) -> pd.DataFrame:
    if not points:
        return pd.DataFrame()
    df = pd.DataFrame([p.model_dump() for p in points])
    df.sort_values("open_time", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def compute_equity_returns(equity_df: pd.DataFrame) -> pd.Series:
    if equity_df.empty:
        return pd.Series()
    return equity_df['equity_usdt'].pct_change().fillna(0)

def compute_running_max_drawdown(equity_df: pd.DataFrame) -> pd.DataFrame:
    if equity_df.empty:
        return equity_df
    df = equity_df.copy()
    df['running_max'] = df['equity_usdt'].cummax()
    df['drawdown_pct'] = (df['equity_usdt'] - df['running_max']) / df['running_max']
    df['drawdown_pct'] = df['drawdown_pct'].fillna(0)
    return df

def validate_equity_curve(equity_df: pd.DataFrame, config) -> None:
    pass
