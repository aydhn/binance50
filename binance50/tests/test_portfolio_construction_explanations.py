import pytest
from binance50.config.models import AppConfig, PortfolioConstructionConfig
from binance50.portfolio.construction.explanations import validate_allocation_explanation
from binance50.core.exceptions import PortfolioConstructionQualityError

@pytest.fixture
def base_config():
    config = AppConfig()
    config.portfolio_construction = PortfolioConstructionConfig()
    return config

def test_validate_explanation_valid(base_config):
    validate_allocation_explanation("Hypothetical allocation based on inverse volatility.", base_config)

def test_validate_explanation_missing(base_config):
    with pytest.raises(PortfolioConstructionQualityError):
        validate_allocation_explanation("", base_config)

def test_validate_explanation_order_like(base_config):
    with pytest.raises(PortfolioConstructionQualityError):
        validate_allocation_explanation("Execute a buy order for 5%.", base_config)

def test_validate_explanation_production_intent(base_config):
    with pytest.raises(PortfolioConstructionQualityError):
        validate_allocation_explanation("Used for production allocation.", base_config)

def test_validate_explanation_live_intent(base_config):
    with pytest.raises(PortfolioConstructionQualityError):
        validate_allocation_explanation("Ready for live trade.", base_config)
