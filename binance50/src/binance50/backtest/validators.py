from typing import Any

import pandas as pd

from .models import BacktestRunResult


def validate_backtest_config(config) -> None:
    pass

def validate_backtest_input_df(df: pd.DataFrame, config) -> None:
    pass

def validate_backtest_result(result: BacktestRunResult, config) -> None:
    pass

def validate_no_execution_dependencies(payload: Any) -> None:
    pass

def validate_no_exchange_order_fields(payload: dict) -> None:
    pass

def validate_no_lookahead_columns(df: pd.DataFrame) -> None:
    pass

def validate_fill_timing(decision_time: int, fill_time: int, config) -> None:
    pass

def validate_no_same_bar_fill(decision_open_time: int, fill_open_time: int, config) -> None:
    pass
