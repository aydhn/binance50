
import pandas as pd
from pydantic import BaseModel

from .models import BacktestEquityPoint


class DrawdownEvent(BaseModel):
    drawdown_id: str
    start_time: int
    trough_time: int
    recovery_time: int | None
    max_drawdown_pct: float
    duration_bars: int
    recovered: bool
    metadata: dict | None = None

def compute_drawdown_series(equity_curve: list[BacktestEquityPoint]) -> pd.DataFrame:
    # Stub
    return pd.DataFrame()

def detect_drawdown_events(equity_curve: list[BacktestEquityPoint]) -> list[DrawdownEvent]:
    return []

def compute_max_drawdown(equity_curve: list[BacktestEquityPoint]) -> float:
    return 0.0

def build_drawdown_report(equity_curve: list[BacktestEquityPoint]) -> dict:
    return {}
