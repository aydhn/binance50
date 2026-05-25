import pandas as pd

from .models import BacktestRunResult


def compute_backtest_input_hash(ohlcv_df: pd.DataFrame, config, strategy_profile: str) -> str:
    return "input_hash_stub"


def compute_backtest_output_hash(result: BacktestRunResult) -> str:
    return "output_hash_stub"


def build_reproducibility_report(result: BacktestRunResult, config) -> dict:
    return {}


def assert_deterministic_run(result_a: BacktestRunResult, result_b: BacktestRunResult) -> None:
    pass
