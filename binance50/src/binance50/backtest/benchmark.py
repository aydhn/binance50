import pandas as pd
from pydantic import BaseModel


class BacktestBenchmarkResult(BaseModel):
    method: str
    symbol: str
    start_time: int
    end_time: int
    start_price: float
    end_price: float
    total_return_pct: float
    benchmark_equity_curve: list
    warnings: list[str] = []


def compute_buy_and_hold_placeholder(
    ohlcv_df: pd.DataFrame, starting_cash_usdt: float, config
) -> BacktestBenchmarkResult:
    # Stub
    return BacktestBenchmarkResult(
        method="buy_and_hold_placeholder",
        symbol="UNKNOWN",
        start_time=0,
        end_time=0,
        start_price=0.0,
        end_price=0.0,
        total_return_pct=0.0,
        benchmark_equity_curve=[],
    )


def compare_backtest_to_benchmark(metrics, benchmark) -> dict:
    return {}


def validate_benchmark_result(result: BacktestBenchmarkResult) -> None:
    pass
