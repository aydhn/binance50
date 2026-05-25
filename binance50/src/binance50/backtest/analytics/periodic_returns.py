from typing import Any

import pandas as pd

from binance50.backtest.analytics.report_models import PeriodicReturnReport
from binance50.config.models import AppConfig


def compute_daily_returns(equity_curve: pd.Series) -> pd.Series:
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        from binance50.core.exceptions import BacktestPeriodicReturnError

        raise BacktestPeriodicReturnError("Datetime index required for periodic returns")
    daily = equity_curve.resample("D").last()
    return daily.pct_change()


def compute_weekly_returns(equity_curve: pd.Series) -> pd.Series:
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        from binance50.core.exceptions import BacktestPeriodicReturnError

        raise BacktestPeriodicReturnError("Datetime index required for periodic returns")
    weekly = equity_curve.resample("W").last()
    return weekly.pct_change()


def compute_monthly_returns(equity_curve: pd.Series) -> pd.Series:
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        from binance50.core.exceptions import BacktestPeriodicReturnError

        raise BacktestPeriodicReturnError("Datetime index required for periodic returns")
    monthly = equity_curve.resample("ME").last()
    return monthly.pct_change()


def compute_quarterly_returns(equity_curve: pd.Series) -> pd.Series:
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        from binance50.core.exceptions import BacktestPeriodicReturnError

        raise BacktestPeriodicReturnError("Datetime index required for periodic returns")
    quarterly = equity_curve.resample("QE").last()
    return quarterly.pct_change()


def compute_yearly_returns(equity_curve: pd.Series) -> pd.Series:
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        from binance50.core.exceptions import BacktestPeriodicReturnError

        raise BacktestPeriodicReturnError("Datetime index required for periodic returns")
    yearly = equity_curve.resample("YE").last()
    return yearly.pct_change()


def build_monthly_return_matrix(monthly_returns: pd.Series) -> pd.DataFrame:
    if monthly_returns.empty:
        return pd.DataFrame()

    df = pd.DataFrame({"return": monthly_returns})
    df["year"] = df.index.year
    df["month"] = df.index.month

    matrix = df.pivot_table(values="return", index="year", columns="month", dropna=False)
    # Add YTD
    matrix["YTD"] = (1 + matrix).prod(axis=1) - 1

    return matrix


def build_calendar_heatmap_table(monthly_returns: pd.Series) -> list[dict[str, Any]]:
    matrix = build_monthly_return_matrix(monthly_returns)
    if matrix.empty:
        return []

    result = []
    for year, row in matrix.iterrows():
        year_data = {"year": int(year)}
        for m in range(1, 13):
            year_data[str(m)] = float(row.get(m, 0.0)) if pd.notna(row.get(m)) else None
        year_data["YTD"] = float(row.get("YTD", 0.0)) if pd.notna(row.get("YTD")) else None
        result.append(year_data)

    return result


def summarize_periodic_returns(periodic_returns: pd.Series) -> dict[str, Any]:
    if periodic_returns.empty:
        return {}

    clean_returns = periodic_returns.dropna()
    if clean_returns.empty:
        return {}

    best_idx = clean_returns.idxmax()
    worst_idx = clean_returns.idxmin()

    positive_count = (clean_returns > 0).sum()
    total_count = len(clean_returns)

    return {
        "best_period": {"date": best_idx.isoformat(), "return": float(clean_returns.loc[best_idx])},
        "worst_period": {
            "date": worst_idx.isoformat(),
            "return": float(clean_returns.loc[worst_idx]),
        },
        "positive_period_ratio": float(positive_count / total_count) if total_count > 0 else None,
    }


def compute_periodic_returns(result: Any, config: AppConfig) -> list[PeriodicReturnReport]:
    reports: list[PeriodicReturnReport] = []
    return reports
