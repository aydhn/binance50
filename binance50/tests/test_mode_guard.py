import pytest

from binance50.config.loader import load_config
from binance50.core.exceptions import ConfigError, InvalidTradingModeError
from binance50.safety.mode_guard import check_mode_consistency, validate_connector_flags


def test_mode_consistency_paper_valid():
    config = load_config()
    # By default it is local_paper_spot with paper trading mode
    check_mode_consistency(config)


def test_mode_consistency_testnet_with_live_mode(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_testnet")
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "live")
    monkeypatch.setenv("BINANCE50_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("BINANCE50_CONFIRM_LIVE_TRADING", "true")

    config = load_config()

    with pytest.raises(InvalidTradingModeError) as exc_info:
        check_mode_consistency(config)
    assert "requires mainnet profile" in str(exc_info.value)


def test_mode_consistency_live_with_paper_mode(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_live")
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "paper")

    config = load_config()

    with pytest.raises(InvalidTradingModeError) as exc_info:
        check_mode_consistency(config)
    assert "cannot be used with paper/backtest" in str(exc_info.value)


def test_readonly_profile_with_order_gateway(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_readonly")
    monkeypatch.setenv("BINANCE50_ORDER_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("BINANCE50_CONNECTION_ENABLED", "true")

    config = load_config()

    with pytest.raises(ConfigError) as exc_info:
        validate_connector_flags(config)
    assert "does not support order placement" in str(exc_info.value)


def test_paper_profile_with_order_gateway(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "local_paper_spot")
    monkeypatch.setenv("BINANCE50_ORDER_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("BINANCE50_CONNECTION_ENABLED", "true")

    config = load_config()

    with pytest.raises(ConfigError) as exc_info:
        validate_connector_flags(config)
    assert "does not support order placement" in str(exc_info.value)


def test_connector_disabled_returns_early(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_readonly")
    monkeypatch.setenv("BINANCE50_ORDER_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("BINANCE50_CONNECTION_ENABLED", "false")

    config = load_config()

    # Should not raise an exception because connection_enabled is false
    validate_connector_flags(config)
