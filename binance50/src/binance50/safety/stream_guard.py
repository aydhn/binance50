from typing import TYPE_CHECKING

from binance50.config.models import AppConfig

if TYPE_CHECKING:
    from binance50.streams.subscription import StreamSubscriptionPlan
from binance50.core.enums import MarketScope


def assert_stream_config_safe(config: AppConfig) -> None:
    from binance50.core.exceptions import StreamConfigError

    if config.streams.market_stream_real_connect_enabled:
        raise StreamConfigError(
            "Real stream connection enabled in config, but not allowed in Phase 9"
        )

    if config.streams.buffer_max_events < 100 or config.streams.buffer_max_events > 1_000_000:
        raise StreamConfigError(
            f"buffer_max_events {config.streams.buffer_max_events} is out of safe range"
        )


def assert_real_stream_connect_allowed(config: AppConfig) -> None:
    from binance50.core.exceptions import StreamConnectionDisabledError

    if not config.streams.market_stream_real_connect_enabled:
        raise StreamConnectionDisabledError("market_stream_real_connect_enabled is false")
    if not config.connector.websocket_enabled:
        raise StreamConnectionDisabledError("connector.websocket_enabled is false")
    if not config.network.real_network_enabled:
        raise StreamConnectionDisabledError("network.real_network_enabled is false")


def assert_subscription_plan_safe(plan: "StreamSubscriptionPlan", config: AppConfig) -> None:
    from binance50.core.exceptions import StreamSubscriptionError

    max_streams = (
        config.streams.max_streams_per_connection_spot
        if plan.market_scope == MarketScope.SPOT
        else config.streams.max_streams_per_connection_usdm
    )
    if len(plan.subscriptions) > max_streams:
        raise StreamSubscriptionError(
            f"Plan stream count {len(plan.subscriptions)} exceeds safe limit {max_streams}"
        )
    if (
        plan.control_message_count > config.streams.max_control_messages_per_second_spot
        and plan.market_scope == MarketScope.SPOT
    ):
        raise StreamSubscriptionError("Control message budget exceeded for SPOT")

    for sub in plan.subscriptions:
        if sub.route.value in ("usdm_private",):
            raise StreamSubscriptionError(
                f"Private routes not allowed in this phase: {sub.route.value}"
            )


def assert_buffer_config_safe(config: AppConfig) -> None:
    assert_stream_config_safe(config)


from typing import Optional


def build_stream_safety_report(
    config: AppConfig, plan: Optional["StreamSubscriptionPlan"] = None
) -> dict:
    status = "safe"
    reasons = []

    if not config.streams.market_stream_real_connect_enabled:
        reasons.append("real_stream_disabled")
    else:
        status = "unsafe"
        reasons.append("real_stream_enabled_in_phase_9")

    try:
        assert_stream_config_safe(config)
    except Exception as e:
        status = "unsafe"
        reasons.append(str(e))

    if plan:
        try:
            assert_subscription_plan_safe(plan, config)
        except Exception as e:
            status = "unsafe"
            reasons.append(str(e))

    return {"status": status, "reasons": reasons, "real_stream_allowed": False}
