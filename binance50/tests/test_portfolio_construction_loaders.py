import pytest
from binance50.config.models import AppConfig, PortfolioConstructionConfig
from binance50.portfolio.construction.loaders import PortfolioConstructionLoader
from binance50.core.exceptions import PortfolioConstructionInputError

@pytest.fixture
def base_config():
    config = AppConfig()
    config.portfolio_construction = PortfolioConstructionConfig()
    return config

def test_extract_selected_candidates_safe(base_config):
    loader = PortfolioConstructionLoader()
    result = {
        "selected_sandbox_candidates": [
            {"symbol": "BTC", "blocked_from_execution": True, "intent": "sandbox_only"}
        ]
    }
    candidates = loader.extract_selected_candidates(result, base_config)
    assert len(candidates) == 1
    assert candidates[0]["symbol"] == "BTC"

def test_extract_selected_candidates_unsafe_unblocked(base_config):
    loader = PortfolioConstructionLoader()
    result = {
        "selected_sandbox_candidates": [
            {"symbol": "BTC", "blocked_from_execution": False, "intent": "sandbox_only"}
        ]
    }
    with pytest.raises(PortfolioConstructionInputError):
        loader.extract_selected_candidates(result, base_config)

def test_extract_selected_candidates_unsafe_intent(base_config):
    loader = PortfolioConstructionLoader()
    result = {
        "selected_sandbox_candidates": [
            {"symbol": "BTC", "blocked_from_execution": True, "intent": "live"}
        ]
    }
    with pytest.raises(PortfolioConstructionInputError):
        loader.extract_selected_candidates(result, base_config)

def test_extract_selected_candidates_min_required(base_config):
    base_config.portfolio_construction.inputs.min_selected_candidates = 2
    loader = PortfolioConstructionLoader()
    result = {
        "selected_sandbox_candidates": [
            {"symbol": "BTC", "blocked_from_execution": True, "intent": "sandbox_only"}
        ]
    }
    with pytest.raises(PortfolioConstructionInputError):
        loader.extract_selected_candidates(result, base_config)
