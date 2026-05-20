from binance50.config.models import AppConfig
from binance50.connectors.adapter_registry import register_adapter
from binance50.connectors.base import (
    RestConnectorProtocol,
    WebSocketConnectorProtocol,
)
from binance50.connectors.capabilities import ConnectorCapabilities
from binance50.connectors.connection_policy import build_connection_policy
from binance50.connectors.endpoint_resolver import build_endpoint_info
from binance50.connectors.response_models import ConnectorHealth
from binance50.connectors.rest_client import BinanceRestClient
from binance50.connectors.websocket_client import BinanceWebSocketClient
from binance50.core.enums import AccountDomain, EnvironmentProfileName, ExchangeName, MarketScope


class BinanceUsdmFuturesAdapter:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.endpoint_info = build_endpoint_info(config)
        self.policy = build_connection_policy(config)
        self.capabilities = ConnectorCapabilities(
            exchange=ExchangeName.BINANCE,
            account_domain=AccountDomain.USDM_FUTURES,
            market_scope=MarketScope.USDM_FUTURES,
            supports_rest=True,
            supports_websocket_market=True,
            supports_websocket_user=True,
            supports_testnet=True,
            supports_mainnet=True,
            supports_readonly=True,
            supports_combined_streams=True,
            supports_raw_streams=True,
            supports_routed_futures_streams=True,
            connection_enabled=self.policy.connection_enabled,
            websocket_enabled=self.policy.websocket_enabled,
            user_data_stream_enabled=self.policy.user_data_stream_enabled,
        )
        self._rest = BinanceRestClient(config, self.endpoint_info, self.capabilities, self.policy)
        self._ws = BinanceWebSocketClient(
            config, self.endpoint_info, self.capabilities, self.policy
        )

    @property
    def exchange_name(self) -> ExchangeName:
        return ExchangeName.BINANCE

    @property
    def account_domain(self) -> AccountDomain:
        return AccountDomain.USDM_FUTURES

    @property
    def market_scope(self) -> MarketScope:
        return MarketScope.USDM_FUTURES

    @property
    def environment_profile(self) -> EnvironmentProfileName:
        return self.endpoint_info.source_profile

    @property
    def rest(self) -> RestConnectorProtocol:
        return self._rest

    @property
    def websocket(self) -> WebSocketConnectorProtocol:
        return self._ws

    def get_health(self) -> ConnectorHealth:
        return self._rest.ping()


register_adapter("binance:usdm_futures", lambda cfg: BinanceUsdmFuturesAdapter(cfg))
