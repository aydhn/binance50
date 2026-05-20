import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import SafetyError
from binance50.safety.rate_limit_guard import (
    assert_rate_limit_config_safe,
    build_rate_limit_safety_report,
    validate_websocket_limits_safe,
)


def test_rate_limit_config_safe():
    config = AppConfig()
    config.network.retry_on_418 = False
    config.network.retry_on_429 = False
    assert_rate_limit_config_safe(config)

    config.network.retry_on_418 = True
    with pytest.raises(SafetyError):
        assert_rate_limit_config_safe(config)

    config.network.retry_on_418 = False
    config.network.retry_on_429 = True
    with pytest.raises(SafetyError):
        assert_rate_limit_config_safe(config)


def test_websocket_limits_safe():
    config = AppConfig()
    validate_websocket_limits_safe(config)

    config.websocket_limits.spot_max_incoming_messages_per_second = 6
    with pytest.raises(SafetyError):
        validate_websocket_limits_safe(config)


def test_build_report():
    config = AppConfig()
    report = build_rate_limit_safety_report(config)
    assert report["config_safe"] is True
