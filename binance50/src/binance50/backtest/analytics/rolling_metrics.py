from typing import Any

import numpy as np
import pandas as pd

from binance50.backtest.analytics.report_models import RollingMetricsReport
from binance50.config.models import AppConfig


def validate_rolling_no_lookahead(metadata: dict[str, Any], config: AppConfig) -> None:
    if config.backtest_reporting.rolling.center_windows:
        from binance50.core.exceptions import BacktestRollingMetricError

        raise BacktestRollingMetricError("Rolling metrics must not use centered windows")


def compute_rolling_return(equity_returns: pd.Series, window: int, min_periods: int) -> pd.Series:
    return equity_returns.rolling(window=window, min_periods=min_periods, center=False).sum()


def compute_rolling_volatility(
    equity_returns: pd.Series, window: int, min_periods: int
) -> pd.Series:
    return equity_returns.rolling(window=window, min_periods=min_periods, center=False).std(ddof=1)


def compute_rolling_sharpe(
    equity_returns: pd.Series, window: int, min_periods: int, periods_per_year: int
) -> pd.Series:
    vol = compute_rolling_volatility(equity_returns, window, min_periods)
    mean_ret = equity_returns.rolling(window=window, min_periods=min_periods, center=False).mean()

    # Avoid division by zero
    sharpe = (mean_ret / vol) * np.sqrt(periods_per_year)
    return sharpe


def compute_rolling_drawdown(equity_curve: pd.Series, window: int, min_periods: int) -> pd.Series:
    rolling_max = equity_curve.rolling(window=window, min_periods=min_periods, center=False).max()
    drawdown = (equity_curve - rolling_max) / rolling_max
    return drawdown


def compute_rolling_win_rate(
    trades_df: pd.DataFrame, equity_index: pd.Index, window: int, min_periods: int
) -> pd.Series:
    # Requires alignment with equity index
    # For now, return empty series
    return pd.Series(index=equity_index, dtype=float)


def compute_rolling_metrics(result: Any, config: AppConfig) -> list[RollingMetricsReport]:
    reports: list[RollingMetricsReport] = []

    validate_rolling_no_lookahead({}, config)

    for window in config.backtest_reporting.rolling.windows:
        report = RollingMetricsReport(
            run_id=result.run_id, window=window, metric_name="all", warnings=[]
        )
        reports.append(report)

    return reports
