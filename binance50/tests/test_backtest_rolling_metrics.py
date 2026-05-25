import pandas as pd

from binance50.backtest.analytics.rolling_metrics import (
    compute_rolling_drawdown,
    compute_rolling_return,
    compute_rolling_sharpe,
    compute_rolling_volatility,
    validate_rolling_no_lookahead,
)
from binance50.config.models import AppConfig


def test_compute_rolling_return():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])
    rolling = compute_rolling_return(returns, window=3, min_periods=2)
    assert len(rolling) == 5
    assert pd.isna(rolling.iloc[0])


def test_compute_rolling_volatility():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])
    rolling = compute_rolling_volatility(returns, window=3, min_periods=2)
    assert len(rolling) == 5


def test_compute_rolling_sharpe():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])
    rolling = compute_rolling_sharpe(returns, window=3, min_periods=2, periods_per_year=365)
    assert len(rolling) == 5


def test_compute_rolling_drawdown():
    equity = pd.Series([100, 110, 105, 120, 115])
    rolling = compute_rolling_drawdown(equity, window=3, min_periods=2)
    assert len(rolling) == 5
    assert (rolling.dropna() <= 0).all()


def test_validate_rolling_no_lookahead():
    config = AppConfig()
    config.backtest_reporting.rolling.center_windows = False

    validate_rolling_no_lookahead({}, config)

    # We can't actually set it to True due to Pydantic Literal constraint,
    # so we just test the safe case.
