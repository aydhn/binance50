import math
from typing import Any

import numpy as np
import pandas as pd

from binance50.backtest.analytics.report_models import AdvancedMetricsReport
from binance50.config.models import AppConfig


def sanitize_metric(value: float | None) -> float | None:
    if value is None:
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return float(value)


def safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0 or math.isnan(denominator) or math.isnan(numerator):
        return None
    return sanitize_metric(numerator / denominator)


def compute_cagr(equity_curve: pd.Series, periods_per_year: int) -> float | None:
    if len(equity_curve) < 2:
        return None
    total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0
    years = len(equity_curve) / periods_per_year
    if years <= 0:
        return None
    try:
        cagr = (1.0 + total_return) ** (1.0 / years) - 1.0
        return sanitize_metric(cagr)
    except Exception:
        return None


def compute_annualized_volatility(returns: pd.Series, periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None
    vol = returns.std(ddof=1)
    if pd.isna(vol):
        return None
    return sanitize_metric(vol * math.sqrt(periods_per_year))


def compute_sharpe_ratio(
    returns: pd.Series, risk_free_rate: float, periods_per_year: int
) -> float | None:
    if len(returns) < 2:
        return None
    excess_returns = returns - (risk_free_rate / periods_per_year)
    mean_return = excess_returns.mean()
    vol = excess_returns.std(ddof=1)

    if vol == 0 or pd.isna(vol) or pd.isna(mean_return):
        return None

    return sanitize_metric((mean_return / vol) * math.sqrt(periods_per_year))


def compute_sortino_ratio(
    returns: pd.Series, risk_free_rate: float, periods_per_year: int
) -> float | None:
    if len(returns) < 2:
        return None
    excess_returns = returns - (risk_free_rate / periods_per_year)
    mean_return = excess_returns.mean()
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) < 2:
        return None

    downside_vol = downside_returns.std(ddof=1)
    if downside_vol == 0 or pd.isna(downside_vol) or pd.isna(mean_return):
        return None

    return sanitize_metric((mean_return / downside_vol) * math.sqrt(periods_per_year))


def compute_calmar_ratio(cagr: float | None, max_drawdown: float | None) -> float | None:
    if cagr is None or max_drawdown is None or max_drawdown == 0:
        return None
    return sanitize_metric(cagr / abs(max_drawdown))


def compute_omega_ratio(returns: pd.Series, threshold: float = 0.0) -> float | None:
    if len(returns) < 2:
        return None
    excess = returns - threshold
    positive_sum = excess[excess > 0].sum()
    negative_sum = abs(excess[excess < 0].sum())

    if negative_sum == 0:
        return None

    return safe_ratio(float(positive_sum), float(negative_sum))


def compute_tail_ratio(returns: pd.Series) -> float | None:
    if len(returns) < 2:
        return None
    p95 = np.percentile(returns.dropna(), 95)
    p05 = np.percentile(returns.dropna(), 5)
    if p05 == 0:
        return None
    return sanitize_metric(abs(p95) / abs(p05))


def compute_var_cvar(
    returns: pd.Series, confidence: float = 0.95
) -> tuple[float | None, float | None]:
    if len(returns) < 2:
        return None, None
    returns_clean = returns.dropna()
    if len(returns_clean) == 0:
        return None, None

    var = np.percentile(returns_clean, (1.0 - confidence) * 100)
    cvar = returns_clean[returns_clean <= var].mean()

    return sanitize_metric(var), sanitize_metric(cvar)


def compute_skew_kurtosis(returns: pd.Series) -> tuple[float | None, float | None]:
    if len(returns) < 3:
        return None, None
    return sanitize_metric(returns.skew()), sanitize_metric(returns.kurtosis())


def compute_payoff_ratio(trades: list[Any]) -> float | None:
    if not trades:
        return None
    winning_trades = [t for t in trades if t.pnl_usdt > 0]
    losing_trades = [t for t in trades if t.pnl_usdt <= 0]

    if not winning_trades or not losing_trades:
        return None

    avg_win = sum(t.pnl_usdt for t in winning_trades) / len(winning_trades)
    avg_loss = abs(sum(t.pnl_usdt for t in losing_trades) / len(losing_trades))

    if avg_loss == 0:
        return None

    return safe_ratio(avg_win, avg_loss)


def compute_recovery_factor(total_return: float | None, max_drawdown: float | None) -> float | None:
    if total_return is None or max_drawdown is None or max_drawdown == 0:
        return None
    return sanitize_metric(total_return / abs(max_drawdown))


def compute_ulcer_index(equity_curve: pd.Series) -> float | None:
    if len(equity_curve) < 2:
        return None
    running_max = equity_curve.cummax()
    drawdowns = (equity_curve - running_max) / running_max
    squared_drawdowns = drawdowns**2
    return sanitize_metric(math.sqrt(squared_drawdowns.mean()))


def compute_advanced_metrics(result: Any, config: AppConfig) -> AdvancedMetricsReport:
    # A complete implementation would parse result.metrics and derive values from equity
    # curve and trades
    # For now, this acts as the interface

    report = AdvancedMetricsReport(run_id=result.run_id, warnings=[])

    # Normally we would fetch real equity curve and calculate

    return report
