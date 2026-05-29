import pytest
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.reproducibility import compute_portfolio_config_hash

def test_compute_portfolio_config_hash_deterministic():
    config = AppConfig()
    hash1 = compute_portfolio_config_hash(config)
    hash2 = compute_portfolio_config_hash(config)
    assert hash1 == hash2
