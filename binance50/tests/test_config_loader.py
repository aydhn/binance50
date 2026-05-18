from binance50.config.loader import load_config
from binance50.core.enums import RuntimeEnvironment, TradingMode


def test_load_default_config(monkeypatch):
    """Test loading the default configuration."""
    # Ensure no relevant env vars are set
    monkeypatch.delenv("BINANCE50_ENV", raising=False)
    monkeypatch.delenv("BINANCE50_TRADING_MODE", raising=False)

    config = load_config("config")
    assert config.project.name == "binance50"
    assert config.runtime.environment == RuntimeEnvironment.LOCAL
    assert config.runtime.trading_mode == TradingMode.PAPER


def test_load_env_override(monkeypatch):
    """Test environment variable overrides."""
    monkeypatch.setenv("BINANCE50_ENV", "testnet")
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "testnet")

    config = load_config("config")
    assert config.runtime.environment == RuntimeEnvironment.TESTNET
    assert config.runtime.trading_mode == TradingMode.TESTNET
