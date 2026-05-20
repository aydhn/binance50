import pytest

from binance50.config.loader import load_config
from binance50.core.exceptions import SafetyError
from binance50.safety.mode_guard import validate_mode_consistency


def test_mode_consistency_paper_valid():
    config = load_config()
    # By default it is local_paper_spot with paper trading mode
    validate_mode_consistency(config)


def test_mode_consistency_testnet_with_live_mode(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_testnet")
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "live")
    monkeypatch.setenv("BINANCE50_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("BINANCE50_CONFIRM_LIVE_TRADING", "true")
    monkeypatch.setenv("BINANCE50_FORCE_PAPER_MODE", "false")
    monkeypatch.setenv("BINANCE50_DRY_RUN", "false")

    config = load_config()

    with pytest.raises(SafetyError) as exc_info:
        validate_mode_consistency(config)
    assert "does not support live trading" in str(exc_info.value)


def test_readonly_profile_with_order_gateway(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_readonly")
    monkeypatch.setenv("BINANCE50_ORDER_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("BINANCE50_CONNECTION_ENABLED", "true")
    # For Phase 4 we need to disable the overall order blocks to even load the config
    monkeypatch.setenv("BINANCE50_DISABLE_ALL_ORDERS", "false")

    config = load_config()

    with pytest.raises(SafetyError) as exc_info:
        validate_mode_consistency(config)
    assert "is readonly but order_gateway is enabled" in str(exc_info.value)
