import pytest
import pandas as pd
from binance50.config.models import AppConfig, PortfolioConstructionConfig
from binance50.portfolio.construction.optimizer_skeleton import run_scipy_slsqp_skeleton

@pytest.fixture
def base_config():
    config = AppConfig()
    config.portfolio_construction = PortfolioConstructionConfig()
    config.portfolio_construction.simulated_capital.max_allocated_capital_pct = 100.0
    config.portfolio_construction.simulated_capital.cash_buffer_pct = 0.0
    return config

def test_scipy_slsqp_skeleton(base_config):
    candidates = [{"symbol": "A"}, {"symbol": "B"}]
    cov = pd.DataFrame([[0.04, 0.0], [0.0, 0.01]], columns=["A", "B"], index=["A", "B"])
    vols = {"A": 20.0, "B": 10.0}

    report = run_scipy_slsqp_skeleton(candidates, cov, vols, base_config)

    assert report.enabled

    if report.scipy_available:
        assert report.success
        assert "A" in report.weights
        assert "B" in report.weights
