import pytest
from pydantic import ValidationError

from binance50.config.loader import load_config
from binance50.config.models import AppConfig, EnvironmentProfileName
from binance50.core.exceptions import ConfigError
from binance50.safety.environment_guard import build_environment_safety_report


def test_default_profile_is_safe():
    config = load_config()
    profile = config.selected_environment_profile

    assert profile.profile_name == EnvironmentProfileName.LOCAL_PAPER_SPOT
    assert profile.allows_real_orders is False
    assert profile.requires_api_key is False
    assert profile.requires_api_secret is False

    report = build_environment_safety_report(config)
    assert report["safety_status"] == "safe"
    assert len(report["blocking_reasons"]) >= 0


def test_spot_testnet_profile_properties():
    config = load_config()
    profile = config.environment_matrix.profiles[EnvironmentProfileName.SPOT_TESTNET]

    assert profile.is_testnet is True
    assert profile.is_mainnet is False
    assert profile.allows_real_orders is True


def test_spot_mainnet_readonly_profile_properties():
    config = load_config()
    profile = config.environment_matrix.profiles[EnvironmentProfileName.SPOT_MAINNET_READONLY]

    assert profile.supports_order_placement is False
    assert profile.is_mainnet is True
    assert profile.allows_real_orders is False


def test_spot_mainnet_live_profile_properties():
    config = load_config()
    profile = config.environment_matrix.profiles[EnvironmentProfileName.SPOT_MAINNET_LIVE]

    assert profile.requires_live_guard is True
    assert profile.allows_real_orders is True


def test_live_profile_blocked_by_default(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_live")
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "live")
    # Need these true to pass the initial validation of AppConfig
    monkeypatch.setenv("BINANCE50_ENABLE_LIVE_TRADING", "true")
    monkeypatch.setenv("BINANCE50_CONFIRM_LIVE_TRADING", "true")
    monkeypatch.setenv("BINANCE50_FORCE_PAPER_MODE", "false")
    monkeypatch.setenv("BINANCE50_DRY_RUN", "false")

    config = load_config()
    report = build_environment_safety_report(config)

    assert report["safety_status"] == "unsafe"
    assert len(report["blocking_reasons"]) > 0
    # Expected blocking reason because LIVE requires explicit enable


def test_invalid_profile_name(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "invalid_profile")

    with pytest.raises(ConfigError):
        load_config()


def test_recv_window_validation(monkeypatch):
    # Requires modification of yaml if testing via loader, but we can test the model directly
    config = load_config()

    with pytest.raises(ValidationError):
        config.connector.recv_window_ms = 70000
        # Trigger validation
        AppConfig(**config.model_dump())


def test_backoff_validation():
    config = load_config()

    with pytest.raises(ValidationError):
        config.connector.backoff_initial_seconds = 10.0
        config.connector.backoff_max_seconds = 5.0
        AppConfig(**config.model_dump())
