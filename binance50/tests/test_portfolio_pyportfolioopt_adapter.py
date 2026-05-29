import pytest
from binance50.config.models import AppConfig, PortfolioConstructionConfig
from binance50.portfolio.construction.adapters.pyportfolioopt_adapter import PyPortfolioOptSkeletonAdapter
from binance50.core.exceptions import PortfolioConstructionOptimizerError

@pytest.fixture
def base_config():
    config = AppConfig()
    config.portfolio_construction = PortfolioConstructionConfig()
    return config

def test_pyportfolioopt_adapter_availability():
    adapter = PyPortfolioOptSkeletonAdapter()
    report = adapter.availability_report()
    assert "available" in report

def test_pyportfolioopt_adapter_safety_check(base_config):
    adapter = PyPortfolioOptSkeletonAdapter()

    # Safe
    base_config.portfolio_construction.allocation_methods.production_optimizer_forbidden = True
    adapter.validate_adapter_sandbox_only(base_config)

    # Unsafe
    base_config.portfolio_construction.allocation_methods.production_optimizer_forbidden = False
    with pytest.raises(PortfolioConstructionOptimizerError):
        adapter.validate_adapter_sandbox_only(base_config)
