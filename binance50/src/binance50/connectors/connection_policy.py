from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigValidationError, SafetyError


class ConnectionPolicy(BaseModel):
    connection_enabled: bool
    websocket_enabled: bool
    user_data_stream_enabled: bool
    order_gateway_enabled: bool
    max_connection_lifetime_hours: int
    websocket_ping_timeout_seconds: int
    websocket_reconnect_before_disconnect_minutes: int
    max_incoming_messages_per_second: int
    request_timeout_seconds: float
    recv_window_ms: int
    max_retry_attempts: int
    backoff_initial_seconds: float
    backoff_max_seconds: float
    rate_limit_backoff_enabled: bool
    circuit_breaker_enabled: bool


def build_connection_policy(config: AppConfig) -> ConnectionPolicy:
    if config.connector.allow_real_network_in_phase5:
        raise SafetyError("allow_real_network_in_phase5 cannot be true in Phase 5")

    return ConnectionPolicy(
        connection_enabled=config.connector.connection_enabled,
        websocket_enabled=config.connector.websocket_enabled,
        user_data_stream_enabled=config.connector.user_data_stream_enabled,
        order_gateway_enabled=config.connector.order_gateway_enabled,
        max_connection_lifetime_hours=config.connector.max_connection_lifetime_hours,
        websocket_ping_timeout_seconds=config.connector.websocket_ping_timeout_seconds,
        websocket_reconnect_before_disconnect_minutes=config.connector.websocket_reconnect_before_disconnect_minutes,
        max_incoming_messages_per_second=config.connector.max_incoming_messages_per_second,
        request_timeout_seconds=config.connector.request_timeout_seconds,
        recv_window_ms=config.connector.recv_window_ms,
        max_retry_attempts=config.connector.max_retry_attempts,
        backoff_initial_seconds=config.connector.backoff_initial_seconds,
        backoff_max_seconds=config.connector.backoff_max_seconds,
        rate_limit_backoff_enabled=config.connector.rate_limit_backoff_enabled,
        circuit_breaker_enabled=config.connector.circuit_breaker_enabled,
    )


def validate_connection_policy(policy: ConnectionPolicy) -> None:
    if policy.max_connection_lifetime_hours < 1 or policy.max_connection_lifetime_hours > 24:
        raise ConfigValidationError("Invalid max_connection_lifetime_hours")


def build_default_disabled_policy(config: AppConfig) -> ConnectionPolicy:
    policy = build_connection_policy(config)
    policy.connection_enabled = False
    policy.websocket_enabled = False
    policy.order_gateway_enabled = False
    policy.user_data_stream_enabled = False
    return policy


def should_connect_rest(config: AppConfig) -> bool:
    return config.connector.connection_enabled


def should_connect_websocket(config: AppConfig) -> bool:
    return config.connector.connection_enabled and config.connector.websocket_enabled


def should_enable_user_stream(config: AppConfig) -> bool:
    return config.connector.connection_enabled and config.connector.user_data_stream_enabled


def should_enable_order_gateway(config: AppConfig) -> bool:
    return config.connector.connection_enabled and config.connector.order_gateway_enabled
