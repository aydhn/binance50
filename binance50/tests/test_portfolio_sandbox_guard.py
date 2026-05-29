import pytest
from binance50.config.models import AppConfig
from binance50.safety.portfolio_sandbox_guard import assert_portfolio_sandbox_config_safe
from binance50.core.exceptions import PortfolioSandboxSafetyError

def test_assert_portfolio_sandbox_config_safe():
    config = AppConfig()
    config.portfolio_sandbox.real_exchange_forbidden = False
    with pytest.raises(PortfolioSandboxSafetyError):
        assert_portfolio_sandbox_config_safe(config)
