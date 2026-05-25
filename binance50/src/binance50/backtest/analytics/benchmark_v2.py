import math
from typing import Any

import numpy as np
import pandas as pd

from binance50.backtest.analytics.advanced_metrics import sanitize_metric
from binance50.backtest.analytics.report_models import BenchmarkComparisonReport
from binance50.config.models import AppConfig


def validate_benchmark_date_range(
    strategy_equity: pd.Series, benchmark_equity: pd.Series, config: AppConfig
) -> None:
    if config.backtest_reporting.benchmark.require_same_date_range:
        if strategy_equity.empty or benchmark_equity.empty:
            return
        # Allow minor differences, but endpoints should match within a few bars
        strat_start, strat_end = strategy_equity.index[0], strategy_equity.index[-1]
        bench_start, bench_end = benchmark_equity.index[0], benchmark_equity.index[-1]

        # Simplified check for example
        if str(strat_start.date()) != str(bench_start.date()) or str(strat_end.date()) != str(
            bench_end.date()
        ):
            from binance50.core.exceptions import BacktestBenchmarkV2Error

            raise BacktestBenchmarkV2Error("Benchmark date range mismatch")


def compute_buy_and_hold_equity(
    ohlcv_df: pd.DataFrame, starting_cash: float, config: AppConfig
) -> pd.Series:
    if ohlcv_df.empty:
        return pd.Series(dtype=float)

    prices = ohlcv_df["close"]
    initial_price = prices.iloc[0]

    if initial_price == 0:
        return pd.Series(index=prices.index, data=starting_cash)

    qty = starting_cash / initial_price
    equity = prices * qty
    return equity


def align_strategy_and_benchmark(
    strategy_equity: pd.Series, benchmark_equity: pd.Series
) -> tuple[pd.Series, pd.Series]:
    # Ensure they share the same index
    common_index = strategy_equity.index.intersection(benchmark_equity.index)
    return strategy_equity.loc[common_index], benchmark_equity.loc[common_index]


def compute_excess_return(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> pd.Series:
    return strategy_returns - benchmark_returns


def compute_tracking_error(
    strategy_returns: pd.Series, benchmark_returns: pd.Series, periods_per_year: int
) -> float | None:
    excess_returns = compute_excess_return(strategy_returns, benchmark_returns)
    te = excess_returns.std(ddof=1)
    if pd.isna(te):
        return None
    return sanitize_metric(te * math.sqrt(periods_per_year))


def compute_information_ratio(excess_returns: pd.Series, periods_per_year: int) -> float | None:
    if len(excess_returns) < 2:
        return None
    mean_excess = excess_returns.mean()
    te = excess_returns.std(ddof=1)

    if te == 0 or pd.isna(te) or pd.isna(mean_excess):
        return None

    return sanitize_metric((mean_excess / te) * math.sqrt(periods_per_year))


def compute_alpha_beta_placeholder(
    strategy_returns: pd.Series, benchmark_returns: pd.Series
) -> tuple[float | None, float | None]:
    if len(strategy_returns) < 2 or len(benchmark_returns) < 2:
        return None, None

    # Placeholder implementation
    # A real implementation would run linear regression
    cov = np.cov(strategy_returns.dropna(), benchmark_returns.dropna())[0][1]
    var = np.var(benchmark_returns.dropna(), ddof=1)

    if var == 0:
        return None, None

    beta = cov / var
    alpha = strategy_returns.mean() - beta * benchmark_returns.mean()

    return sanitize_metric(alpha), sanitize_metric(beta)


def compute_benchmark_v2(result: Any, config: AppConfig) -> BenchmarkComparisonReport:
    report = BenchmarkComparisonReport(
        run_id=result.run_id,
        benchmark_label=config.backtest_reporting.benchmark.benchmark_label,
        warnings=[],
    )
    return report
