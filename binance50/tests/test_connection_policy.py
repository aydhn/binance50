import pytest

from binance50.config.loader import load_config
from binance50.connectors.connection_policy import (
    build_connection_policy,
    should_connect_rest,
    should_connect_websocket,
)
from binance50.core.exceptions import SafetyError


def test_default_connection_policy() -> None:
    config = load_config()
    policy = build_connection_policy(config)

    assert policy.connection_enabled is False
    assert policy.websocket_enabled is False
    assert policy.order_gateway_enabled is False
    assert policy.max_connection_lifetime_hours == 24

    assert should_connect_rest(config) is False
    assert should_connect_websocket(config) is False


def test_phase5_network_blocked() -> None:
    config = load_config()
    config.connector.allow_real_network_in_phase5 = True

    with pytest.raises(SafetyError, match="cannot be true in Phase 5"):
        build_connection_policy(config)
