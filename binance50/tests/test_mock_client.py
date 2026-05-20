from binance50.connectors.mock_client import (
    MockExchangeAdapter,
    MockRestClient,
    MockWebSocketClient,
)


def test_mock_rest_client() -> None:
    client = MockRestClient()
    assert client.is_enabled() is True
    health = client.ping()
    assert health.status == "mock_success"
    assert health.connected is True

    report = health.redacted_dump()
    assert "mock_success" in str(report)


def test_mock_websocket_client() -> None:
    client = MockWebSocketClient()
    assert client.is_enabled() is True

    # Should not raise exception
    client.connect()

    url = client.build_stream_url(["btcusdt@trade"])
    assert "btcusdt" in url


def test_mock_adapter() -> None:
    adapter = MockExchangeAdapter()
    assert adapter.rest.is_enabled() is True
    assert adapter.websocket.is_enabled() is True
    assert adapter.get_health().status == "mock_success"
