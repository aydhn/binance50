from datetime import datetime

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.time_utils import get_utc_now
from binance50.streams.event_types import StreamRoute, StreamType
from binance50.streams.stream_names import build_stream_name
from binance50.connectors.stream_names import build_combined_stream_path


class StreamSubscription(BaseModel):
    symbol: str
    stream_type: StreamType
    interval: str | None = None
    stream_name: str
    market_scope: MarketScope
    route: StreamRoute
    enabled: bool = True

class StreamSubscriptionPlan(BaseModel):
    plan_id: str
    market_scope: MarketScope
    use_combined: bool
    subscriptions: list[StreamSubscription]
    raw_stream_names: list[str]
    combined_path: str | None = None
    connection_count: int = 1
    control_message_count: int = 0
    estimated_message_rate: int = 0
    created_at_utc: datetime = Field(default_factory=get_utc_now)
    warnings: list[str] = Field(default_factory=list)

def build_subscription_plan(
    symbols: list[str],
    stream_types: list[StreamType],
    market_scope: MarketScope,
    config: AppConfig,
    interval: str | None = None
) -> StreamSubscriptionPlan:
    if not symbols:
        raise ValueError("symbols list cannot be empty")
    if not stream_types:
        raise ValueError("stream_types list cannot be empty")

    if len(symbols) > config.streams.max_symbols_per_stream_plan:
        raise ValueError(f"Symbols count exceeds max_symbols_per_stream_plan ({config.streams.max_symbols_per_stream_plan})")

    if not interval and StreamType.kline in stream_types:
        interval = config.streams.default_kline_interval

    subs = []
    raw_names = []

    # Simple route logic for now (Spot vs USDM)
    route = StreamRoute.spot_raw
    if market_scope == MarketScope.SPOT and config.streams.use_combined_streams:
        route = StreamRoute.spot_combined
    elif market_scope == MarketScope.USDM_FUTURES:
        route = StreamRoute.usdm_market

    for sym in symbols:
        for st in stream_types:
            if st.value not in config.streams.allowed_stream_types:
                continue # or warn

            if st == StreamType.mark_price and market_scope != MarketScope.USDM_FUTURES:
                continue # not valid for spot

            stream_name = build_stream_name(sym, st, interval, market_scope=market_scope)
            subs.append(StreamSubscription(
                symbol=sym.upper(),
                stream_type=st,
                interval=interval if st == StreamType.kline else None,
                stream_name=stream_name,
                market_scope=market_scope,
                route=route,
                enabled=True
            ))
            raw_names.append(stream_name)

    use_combined = config.streams.use_combined_streams
    combined_path = build_combined_stream_path(raw_names) if use_combined else None

    # Estimate logic could go here
    plan = StreamSubscriptionPlan(
        plan_id=f"plan_{int(get_utc_now().timestamp())}",
        market_scope=market_scope,
        use_combined=use_combined,
        subscriptions=subs,
        raw_stream_names=raw_names,
        combined_path=combined_path
    )

    validate_subscription_plan(plan, config)
    return plan

def split_subscriptions_into_connections(plan: StreamSubscriptionPlan, config: AppConfig) -> list[list[StreamSubscription]]:
    max_streams = config.streams.max_streams_per_connection_spot if plan.market_scope == MarketScope.SPOT else config.streams.max_streams_per_connection_usdm
    res = []
    current = []
    for sub in plan.subscriptions:
        current.append(sub)
        if len(current) >= max_streams:
            res.append(current)
            current = []
    if current:
        res.append(current)
    return res

def build_subscribe_payload(subscriptions: list[StreamSubscription], request_id: int = 1) -> dict:
    return {
        "method": "SUBSCRIBE",
        "params": [sub.stream_name for sub in subscriptions],
        "id": request_id
    }

def build_unsubscribe_payload(subscriptions: list[StreamSubscription], request_id: int = 1) -> dict:
    return {
        "method": "UNSUBSCRIBE",
        "params": [sub.stream_name for sub in subscriptions],
        "id": request_id
    }

def build_list_subscriptions_payload(request_id: int = 1) -> dict:
    return {
        "method": "LIST_SUBSCRIPTIONS",
        "id": request_id
    }

def build_set_property_payload(combined: bool, request_id: int = 1) -> dict:
    return {
        "method": "SET_PROPERTY",
        "params": [
            "combined",
            combined
        ],
        "id": request_id
    }

def validate_subscription_plan(plan: StreamSubscriptionPlan, config: AppConfig) -> None:
    from binance50.core.exceptions import StreamSubscriptionError

    max_limit = config.streams.max_streams_per_connection_spot if plan.market_scope == MarketScope.SPOT else config.streams.max_streams_per_connection_usdm
    if len(plan.subscriptions) > max_limit:
        raise StreamSubscriptionError(f"Subscription count {len(plan.subscriptions)} exceeds max limit {max_limit}")

    for sub in plan.subscriptions:
        if sub.stream_type.value not in config.streams.allowed_stream_types:
            raise StreamSubscriptionError(f"Stream type {sub.stream_type.value} not allowed")
