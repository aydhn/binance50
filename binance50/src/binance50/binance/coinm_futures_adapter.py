from binance50.config.models import AppConfig
from binance50.connectors.adapter_registry import register_adapter
from binance50.connectors.base import (
    ExchangeAdapterProtocol,
    RestConnectorProtocol,
    WebSocketConnectorProtocol,
)
from binance50.connectors.response_models import ConnectorHealth
from binance50.core.enums import AccountDomain, EnvironmentProfileName, ExchangeName, MarketScope
from binance50.core.exceptions import UnsupportedFeatureError


class BinanceCoinmFuturesAdapter:
    def __init__(self, config: AppConfig) -> None:
        pass

    @property
    def exchange_name(self) -> ExchangeName:
        return ExchangeName.BINANCE

    @property
    def account_domain(self) -> AccountDomain:
        return AccountDomain.COINM_FUTURES

    @property
    def market_scope(self) -> MarketScope:
        return MarketScope.COINM_FUTURES

    @property
    def environment_profile(self) -> EnvironmentProfileName:
        return EnvironmentProfileName.COINM_FUTURES_PLACEHOLDER

    @property
    def rest(self) -> RestConnectorProtocol:
        raise UnsupportedFeatureError("COIN-M futures are not implemented")

    @property
    def websocket(self) -> WebSocketConnectorProtocol:
        raise UnsupportedFeatureError("COIN-M futures are not implemented")

    def get_health(self) -> ConnectorHealth:
        raise UnsupportedFeatureError("COIN-M futures are not implemented")


# Mypy workaround: explicitly type the lambda return
def _create_coinm_adapter(cfg: AppConfig) -> ExchangeAdapterProtocol:
    return BinanceCoinmFuturesAdapter(cfg)


register_adapter("binance:coinm_futures", _create_coinm_adapter)
