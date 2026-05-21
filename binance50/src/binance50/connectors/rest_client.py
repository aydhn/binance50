from typing import Any

from binance50.config.models import AppConfig
from binance50.connectors.capabilities import ConnectorCapabilities
from binance50.connectors.connection_policy import ConnectionPolicy
from binance50.connectors.endpoint_resolver import EndpointInfo
from binance50.connectors.response_models import ConnectorHealth
from binance50.core.exceptions import ConnectorDisabledError, UnsupportedFeatureError


class BinanceRestClient:
    def __init__(
        self,
        config: AppConfig,
        endpoint_info: EndpointInfo,
        capabilities: ConnectorCapabilities,
        policy: ConnectionPolicy,
        httpx_client: Any = None,
    ) -> None:
        self.config = config
        self.endpoint_info = endpoint_info
        self.capabilities = capabilities
        self.policy = policy
        self.httpx_client = httpx_client

    def is_enabled(self) -> bool:
        return self.policy.connection_enabled

    def get_capabilities(self) -> ConnectorCapabilities:
        return self.capabilities

    def get_endpoint_info(self) -> EndpointInfo:
        return self.endpoint_info

    def ping(self) -> ConnectorHealth:
        from binance50.core.enums import (
            AccountDomain,
            ExchangeName,
            MarketScope,
        )

        return ConnectorHealth(
            enabled=self.is_enabled(),
            connected=False,
            connector_type="rest",
            exchange=ExchangeName.BINANCE,
            environment_profile=self.endpoint_info.source_profile,
            account_domain=AccountDomain.SPOT,
            market_scope=MarketScope.SPOT,
            status="skeleton",
            message="Phase 5 skeleton",
            last_check_utc="1970-01-01T00:00:00Z",
            capabilities=self.capabilities,
        )

    def build_public_kline_request(
        self,
        symbol: str,
        market_scope: "MarketScope",
        interval: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
        limit: int | None = None,
    ) -> Any:
        from binance50.connectors.request_models import ConnectorRequest, HttpMethod
        from binance50.core.enums import MarketScope

        path = (
            self.config.market_data.spot_klines_path
            if market_scope == MarketScope.SPOT
            else self.config.market_data.usdm_klines_path
        )

        params = {"symbol": symbol.upper(), "interval": interval}
        if start_time_ms is not None:
            params["startTime"] = start_time_ms
        if end_time_ms is not None:
            params["endTime"] = end_time_ms
        if limit is not None:
            params["limit"] = limit

        return ConnectorRequest(
            method=HttpMethod.GET,
            path=path,
            params=params,
            is_signed=False,
            weight=1,
            market_scope=market_scope,
        )

    def build_request(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def send_request(self, *args: Any, **kwargs: Any) -> Any:
        if not self.is_enabled():
            raise ConnectorDisabledError()
        if self.config.network.real_network_enabled:
            from binance50.core.exceptions import RealNetworkDisabledError

            raise RealNetworkDisabledError()
        raise UnsupportedFeatureError("Real REST calls are not implemented in Phase 5")

    def close(self) -> None:
        pass
