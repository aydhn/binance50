from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamRoute, StreamType
from binance50.streams.subscription import StreamSubscriptionPlan


def resolve_stream_route(
    market_scope: MarketScope, stream_type: StreamType, config: AppConfig
) -> StreamRoute:
    if market_scope == MarketScope.SPOT:
        if config.streams.use_combined_streams:
            return StreamRoute.spot_combined
        return StreamRoute.spot_raw
    elif market_scope == MarketScope.USDM_FUTURES:
        if stream_type in (StreamType.mark_price, StreamType.force_order):
            # Often handled on the same stream endpoint, but conceptually different
            return StreamRoute.usdm_market
        return StreamRoute.usdm_market
    return StreamRoute.unknown


def resolve_ws_base_for_route(route: StreamRoute, config: AppConfig) -> str | None:
    # Requires an endpoint resolver in reality, but here we can mock or use basic fallback
    if route in (StreamRoute.spot_raw, StreamRoute.spot_combined):
        return "wss://stream.binance.com:9443"
    elif route == StreamRoute.usdm_market:
        return "wss://fstream.binance.com"
    return None


def build_full_stream_url(plan: StreamSubscriptionPlan, config: AppConfig) -> str:
    # Basic route from first sub
    if not plan.subscriptions:
        raise ValueError("Empty plan")

    route = plan.subscriptions[0].route
    base_url = resolve_ws_base_for_route(route, config) or ""

    if plan.use_combined and plan.combined_path:
        return f"{base_url}{plan.combined_path}"

    # Raw route
    from binance50.streams.stream_names import build_raw_stream_path

    path = build_raw_stream_path(plan.raw_stream_names[0])
    return f"{base_url}{path}"


def validate_route_supported(
    route: StreamRoute, market_scope: MarketScope, config: AppConfig
) -> None:
    from binance50.core.exceptions import StreamRouteError

    if route == StreamRoute.unknown:
        raise StreamRouteError("Unknown stream route")
    if route in (StreamRoute.usdm_private,) and market_scope == MarketScope.SPOT:
        raise StreamRouteError("USDM private route invalid for SPOT")
    # Add more logic as needed
