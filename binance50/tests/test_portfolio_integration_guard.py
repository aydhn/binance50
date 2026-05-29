import pytest
from binance50.config.models import AppConfig
from binance50.safety.portfolio_integration_guard import assert_no_signal_engine_write
from binance50.core.exceptions import PortfolioIntegrationForbiddenError

def test_assert_no_signal_engine_write():
    config = AppConfig()
    config.portfolio_sandbox.sandbox_output.write_to_signal_engine_forbidden = False
    with pytest.raises(PortfolioIntegrationForbiddenError):
        assert_no_signal_engine_write(config)
