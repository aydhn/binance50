from binance50.connectors.base import (
    EndpointInfoProtocol,
    RestConnectorProtocol,
    WebSocketConnectorProtocol,
)
from binance50.connectors.capabilities import ConnectorCapabilities
from binance50.connectors.endpoint_resolver import EndpointInfo
from binance50.connectors.response_models import ConnectorHealth
from binance50.core.enums import AccountDomain, EnvironmentProfileName, ExchangeName, MarketScope
from binance50.core.exceptions import ConnectorDisabledError


class DisabledRestClient:
    def is_enabled(self) -> bool:
        return False

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            exchange=ExchangeName.BINANCE,
            account_domain=AccountDomain.SPOT,
            market_scope=MarketScope.SPOT,
        )

    def get_endpoint_info(self) -> EndpointInfoProtocol:
        return EndpointInfo(source_profile=EnvironmentProfileName.LOCAL_PAPER_SPOT)

    def ping(self) -> ConnectorHealth:
        return ConnectorHealth(
            enabled=False,
            connected=False,
            connector_type="rest",
            exchange=ExchangeName.BINANCE,
            environment_profile=EnvironmentProfileName.LOCAL_PAPER_SPOT,
            account_domain=AccountDomain.SPOT,
            market_scope=MarketScope.SPOT,
            status="disabled_safe",
            message="Connector disabled by default; no external network calls allowed.",
            last_check_utc="1970-01-01T00:00:00Z",
            capabilities=self.get_capabilities(),
        )

    def close(self) -> None:
        pass


class DisabledWebSocketClient:
    def is_enabled(self) -> bool:
        return False

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            exchange=ExchangeName.BINANCE,
            account_domain=AccountDomain.SPOT,
            market_scope=MarketScope.SPOT,
        )

    def build_stream_url(self, streams: list[str], combined: bool = True) -> str:
        # Can build url safely but won't connect
        if combined:
            from binance50.connectors.stream_names import build_combined_stream_path

            return build_combined_stream_path(streams)
        from binance50.connectors.stream_names import build_raw_stream_path

        return build_raw_stream_path(streams[0])

    def connect(self) -> None:
        raise ConnectorDisabledError()

    def close(self) -> None:
        pass


class DisabledExchangeAdapter:
    @property
    def exchange_name(self) -> ExchangeName:
        return ExchangeName.BINANCE

    @property
    def account_domain(self) -> AccountDomain:
        return AccountDomain.SPOT

    @property
    def market_scope(self) -> MarketScope:
        return MarketScope.SPOT

    @property
    def environment_profile(self) -> EnvironmentProfileName:
        return EnvironmentProfileName.LOCAL_PAPER_SPOT

    @property
    def rest(self) -> RestConnectorProtocol:
        return DisabledRestClient()

    @property
    def websocket(self) -> WebSocketConnectorProtocol:
        return DisabledWebSocketClient()

    def get_health(self) -> ConnectorHealth:
        return self.rest.ping()
