import pytest
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.explanations import validate_explanation
from binance50.core.exceptions import PortfolioSandboxQualityError

def test_validate_explanation_rejects_order_language():
    config = AppConfig()
    with pytest.raises(PortfolioSandboxQualityError, match="Actionable/order language detected"):
        validate_explanation("Buy BTCUSDT now", config)
