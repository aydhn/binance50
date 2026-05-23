import pytest
from binance50.config.models import AppConfig

@pytest.fixture
def config() -> AppConfig:
    return AppConfig()
