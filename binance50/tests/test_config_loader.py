import pytest

from binance50.config.loader import load_config
from binance50.core.enums import RuntimeEnvironment, TradingMode
from binance50.core.exceptions import ConfigError


def test_load_default_config():
    """Test loading default configuration."""
    config = load_config("config")

    assert config.project.name == "binance50"
    assert config.runtime.environment == RuntimeEnvironment.LOCAL
    assert config.runtime.trading_mode == TradingMode.PAPER
    assert config.safety.enable_live_trading is False


def test_load_env_override(monkeypatch):
    """Test environment variable overrides."""
    monkeypatch.setenv("BINANCE50_ENV", "testnet")
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "testnet")
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_testnet")

    config = load_config("config")
    assert config.runtime.environment == RuntimeEnvironment.TESTNET
    assert config.runtime.trading_mode == TradingMode.TESTNET


def test_load_invalid_directory():
    """Test loading from an invalid directory."""
    with pytest.raises(ConfigError):
        load_config("invalid_dir")


def test_invalid_exchange_override(monkeypatch):
    """Test setting an unsupported exchange."""
    monkeypatch.setenv("BINANCE50_EXCHANGE", "coinbase")

    with pytest.raises(ConfigError):
        load_config("config")
