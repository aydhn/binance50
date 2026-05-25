import math

import numpy as np
import pandas as pd

from binance50.backtest.analytics.advanced_metrics import (
    compute_annualized_volatility,
    compute_cagr,
    compute_calmar_ratio,
    compute_omega_ratio,
    compute_payoff_ratio,
    compute_recovery_factor,
    compute_sharpe_ratio,
    compute_skew_kurtosis,
    compute_sortino_ratio,
    compute_tail_ratio,
    compute_ulcer_index,
    compute_var_cvar,
    safe_ratio,
    sanitize_metric,
)


class MockTrade:
    def __init__(self, pnl):
        self.pnl_usdt = pnl


def test_safe_ratio():
    assert safe_ratio(10, 2) == 5.0
    assert safe_ratio(10, 0) is None
    assert safe_ratio(math.nan, 2) is None


def test_sanitize_metric():
    assert sanitize_metric(1.5) == 1.5
    assert sanitize_metric(math.nan) is None
    assert sanitize_metric(math.inf) is None
    assert sanitize_metric(None) is None


def test_compute_cagr():
    equity = pd.Series([100, 110, 121])
    # 2 bars / 365 = 2/365 years.
    # We just ensure it runs safely without blowing up
    cagr = compute_cagr(equity, 365)
    assert cagr is not None

    empty = pd.Series([])
    assert compute_cagr(empty, 365) is None


def test_compute_annualized_volatility():
    returns = pd.Series([0.01, -0.02, 0.03])
    vol = compute_annualized_volatility(returns, 365)
    assert vol is not None
    assert vol > 0


def test_compute_sharpe_ratio():
    returns = pd.Series([0.01, -0.02, 0.03])
    sharpe = compute_sharpe_ratio(returns, 0.0, 365)
    assert sharpe is not None


def test_compute_sortino_ratio():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01])
    sortino = compute_sortino_ratio(returns, 0.0, 365)
    assert sortino is not None


def test_compute_calmar_ratio():
    assert compute_calmar_ratio(0.10, -0.05) == 2.0
    assert compute_calmar_ratio(None, -0.05) is None
    assert compute_calmar_ratio(0.10, 0.0) is None


def test_compute_omega_ratio():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01])
    omega = compute_omega_ratio(returns)
    assert omega is not None


def test_compute_tail_ratio():
    returns = pd.Series(np.random.normal(0, 0.01, 100))
    tail = compute_tail_ratio(returns)
    assert tail is not None


def test_compute_var_cvar():
    returns = pd.Series(np.random.normal(0, 0.01, 100))
    var, cvar = compute_var_cvar(returns)
    assert var is not None
    assert cvar is not None
    assert cvar <= var


def test_compute_skew_kurtosis():
    returns = pd.Series(np.random.normal(0, 0.01, 100))
    skew, kurtosis = compute_skew_kurtosis(returns)
    assert skew is not None
    assert kurtosis is not None


def test_compute_payoff_ratio():
    trades = [MockTrade(10), MockTrade(20), MockTrade(-15)]
    payoff = compute_payoff_ratio(trades)
    assert payoff == 1.0


def test_compute_recovery_factor():
    assert compute_recovery_factor(0.50, -0.10) == 5.0


def test_compute_ulcer_index():
    equity = pd.Series([100, 110, 105, 120])
    ulcer = compute_ulcer_index(equity)
    assert ulcer is not None
