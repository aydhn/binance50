import pytest
from binance50.config.models import AppConfig, PortfolioConstructionConfig
from binance50.portfolio.construction.adapters.scipy_slsqp_adapter import SciPySLSQPPortfolioAdapter

@pytest.fixture
def base_config():
    config = AppConfig()
    config.portfolio_construction = PortfolioConstructionConfig()
    return config

def test_scipy_adapter_availability():
    adapter = SciPySLSQPPortfolioAdapter()
    report = adapter.availability_report()
    assert "available" in report

def test_scipy_adapter_bounds(base_config):
    adapter = SciPySLSQPPortfolioAdapter()
    base_config.portfolio_construction.equal_weight.max_single_weight_pct = 40.0
    bounds = adapter.build_bounds(3, base_config)
    assert len(bounds) == 3
    for b in bounds:
        assert b == (0.0, 0.4)
