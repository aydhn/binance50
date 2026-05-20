import pytest

from binance50.connectors.disabled_client import (
    ConnectorDisabledError,
    DisabledExchangeAdapter,
    DisabledRestClient,
    DisabledWebSocketClient,
)
from binance50.connectors.order_gateway import DisabledOrderGateway
from binance50.core.exceptions import OrderPathDisabledError


def test_disabled_rest_client() -> None:
    client = DisabledRestClient()
    assert client.is_enabled() is False
    health = client.ping()
    assert health.status == "disabled_safe"
    assert health.connected is False

    report = health.redacted_dump()
    assert "api_key" not in report


def test_disabled_websocket_client() -> None:
    client = DisabledWebSocketClient()
    assert client.is_enabled() is False

    with pytest.raises(ConnectorDisabledError):
        client.connect()

    # should build url without connecting
    url = client.build_stream_url(["btcusdt@trade"])
    assert "btcusdt" in url


def test_disabled_order_gateway() -> None:
    gateway = DisabledOrderGateway()
    assert gateway.is_enabled() is False

    with pytest.raises(OrderPathDisabledError):
        gateway.submit_order()


def test_disabled_adapter() -> None:
    adapter = DisabledExchangeAdapter()
    assert adapter.rest.is_enabled() is False
    assert adapter.websocket.is_enabled() is False
    assert adapter.get_health().connected is False
