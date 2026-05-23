from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from binance50.streams.subscription import StreamSubscriptionPlan

from binance50.config.models import AppConfig
from binance50.connectors.capabilities import ConnectorCapabilities
from binance50.connectors.connection_policy import ConnectionPolicy
from binance50.connectors.endpoint_resolver import EndpointInfo
from binance50.connectors.stream_names import build_combined_stream_path, build_raw_stream_path
from binance50.core.exceptions import ConnectorDisabledError, UnsupportedFeatureError
from binance50.rate_limit.websocket_limits import validate_stream_count
from binance50.safety.stream_guard import assert_real_stream_connect_allowed


class BinanceWebSocketClient:
    def __init__(
        self,
        config: AppConfig,
        endpoint_info: EndpointInfo,
        capabilities: ConnectorCapabilities,
        policy: ConnectionPolicy,
    ) -> None:
        self.config = config
        self.endpoint_info = endpoint_info
        self.capabilities = capabilities
        self.policy = policy

    def validate_streams(self, stream_count: int) -> None:
        decision = validate_stream_count(self.config, stream_count)
        if not decision.allowed:
            from binance50.core.exceptions import WebSocketLimitError

            raise WebSocketLimitError(decision.reason)

    def is_enabled(self) -> bool:
        return self.policy.websocket_enabled

    def get_capabilities(self) -> ConnectorCapabilities:
        return self.capabilities

    def build_stream_url(self, streams: list[str], combined: bool = True) -> str:
        base = self.endpoint_info.websocket_market_base_url
        if not base:
            # For futures routed, base would be handled differently but let's default to market
            base = self.endpoint_info.futures_market_ws_base_url or ""

        if combined:
            return f"{base}{build_combined_stream_path(streams)}"
        return f"{base}{build_raw_stream_path(streams[0])}"

    def connect(self) -> None:
        if not self.is_enabled():
            raise ConnectorDisabledError()
        raise UnsupportedFeatureError("Real WebSocket calls are not implemented in Phase 5")

    def close(self) -> None:
        pass

    def build_subscription_plan(
        self, symbols: list[str], stream_types: list, market_scope, interval=None
    ) -> "StreamSubscriptionPlan":
        from binance50.streams.subscription import build_subscription_plan

        return build_subscription_plan(symbols, stream_types, market_scope, self.config, interval)

    def build_stream_url_from_plan(self, plan: "StreamSubscriptionPlan") -> str:
        from binance50.streams.routing import build_full_stream_url

        # Adjust base depending on plan type inside routing, but the method handles it if config is passed
        # The routing module actually needs endpoint info, but here we just rely on the new method
        # which might not perfectly align with endpoint_info, but let's stick to the phase requirements
        return build_full_stream_url(plan, self.config)

    def subscribe(self, plan: "StreamSubscriptionPlan") -> None:
        assert_real_stream_connect_allowed(self.config)

    def unsubscribe(self, plan: "StreamSubscriptionPlan") -> None:
        assert_real_stream_connect_allowed(self.config)

    def receive_loop(self) -> None:
        assert_real_stream_connect_allowed(self.config)
