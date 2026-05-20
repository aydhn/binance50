import pytest

from binance50.config.loader import load_config
from binance50.core.exceptions import OrderPathDisabledError, SafetyError
from binance50.safety.connector_guard import (
    assert_connector_allowed,
    assert_order_gateway_still_blocked_by_default,
    assert_user_data_stream_allowed,
    assert_websocket_connection_allowed,
    build_connector_safety_report,
)


def test_default_config_connector_allowed_as_disabled() -> None:
    config = load_config()
    # It should raise SafetyError because connection_enabled is false
    with pytest.raises(SafetyError, match="disabled by config"):
        assert_connector_allowed(config)


def test_connection_enabled_paper_requires_mock() -> None:
    config = load_config()
    config.connector.connection_enabled = True
    config.connector.mock_enabled = False

    with pytest.raises(SafetyError, match="Real connector not allowed in paper mode"):
        assert_connector_allowed(config)

    config.connector.mock_enabled = True
    # Now it should pass
    assert_connector_allowed(config)


def test_websocket_blocked() -> None:
    config = load_config()
    config.connector.connection_enabled = True
    config.connector.mock_enabled = True
    config.connector.websocket_enabled = False

    with pytest.raises(SafetyError, match="WebSocket is disabled"):
        assert_websocket_connection_allowed(config)


def test_user_data_stream_blocked_without_credentials() -> None:
    config = load_config()
    config.connector.connection_enabled = True
    config.connector.mock_enabled = True
    config.connector.websocket_enabled = True
    config.connector.user_data_stream_enabled = True

    with pytest.raises(SafetyError, match="User data stream requires API credentials"):
        assert_user_data_stream_allowed(config)


def test_order_gateway_blocked() -> None:
    config = load_config()
    config.connector.order_gateway_enabled = True

    with pytest.raises(OrderPathDisabledError, match="Order gateway is structurally blocked"):
        assert_order_gateway_still_blocked_by_default(config)


def test_safety_report_no_secrets() -> None:
    config = load_config()
    report = build_connector_safety_report(config)

    assert "connection_enabled" in report
    assert "mock_enabled" in report
    assert "api_key" not in report
    assert "api_secret" not in report
