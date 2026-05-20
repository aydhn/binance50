from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import OrderPathDisabledError, SafetyError


def assert_connector_allowed(config: AppConfig) -> None:
    if not config.connector.connection_enabled:
        raise SafetyError("Connector is disabled by config (connection_enabled=false)")
    if config.selected_environment_profile.is_paper and not config.connector.mock_enabled:
        raise SafetyError(
            "Real connector not allowed in paper mode. Use mock_enabled=true or disable connector."
        )
    if config.connector.allow_real_network_in_phase5:
        raise SafetyError(
            "Phase 5 explicitly blocks real network calls. "
            "allow_real_network_in_phase5 must be false."
        )


def assert_rest_connection_allowed(config: AppConfig) -> None:
    assert_connector_allowed(config)


def assert_websocket_connection_allowed(config: AppConfig) -> None:
    assert_connector_allowed(config)
    if not config.connector.websocket_enabled:
        raise SafetyError("WebSocket is disabled by config")


def assert_user_data_stream_allowed(config: AppConfig) -> None:
    assert_websocket_connection_allowed(config)
    if not config.connector.user_data_stream_enabled:
        raise SafetyError("User data stream is disabled by config")
    # Needs credentials
    if not config.credentials.binance.api_key or not config.credentials.binance.api_secret:
        raise SafetyError("User data stream requires API credentials")


def assert_order_gateway_still_blocked_by_default(config: AppConfig) -> None:
    if config.connector.order_gateway_enabled:
        raise OrderPathDisabledError("Order gateway is structurally blocked in Phase 5 default.")


def build_connector_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "connection_enabled": config.connector.connection_enabled,
        "mock_enabled": config.connector.mock_enabled,
        "websocket_enabled": config.connector.websocket_enabled,
        "order_gateway_enabled": config.connector.order_gateway_enabled,
        "real_network_allowed": config.connector.allow_real_network_in_phase5,
        "profile_is_paper": config.selected_environment_profile.is_paper,
    }
