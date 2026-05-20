from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig


class WebSocketLimitDecision(BaseModel):
    allowed: bool
    reason: str | None = None
    incoming_message_limit_per_second: int
    stream_limit: int
    current_stream_count: int
    requested_stream_count: int
    control_message_budget_per_second: int
    connection_lifetime_hours: int
    reconnect_deadline_utc: datetime
    warnings: list[str] = Field(default_factory=list)


def get_ws_limits_for_scope(config: AppConfig) -> dict:
    scope = config.runtime.market_scope
    limits = config.websocket_limits
    if scope == "spot":
        return {
            "max_incoming": limits.spot_max_incoming_messages_per_second,
            "max_streams": limits.spot_max_streams_per_connection,
        }
    else:
        return {
            "max_incoming": limits.usdm_max_incoming_messages_per_second,
            "max_streams": limits.usdm_max_streams_per_connection,
        }


def validate_stream_count(config: AppConfig, stream_count: int) -> WebSocketLimitDecision:
    limits = get_ws_limits_for_scope(config)
    allowed = stream_count <= limits["max_streams"]
    now = datetime.now(UTC)
    return WebSocketLimitDecision(
        allowed=allowed,
        reason="Stream limit exceeded" if not allowed else None,
        incoming_message_limit_per_second=limits["max_incoming"],
        stream_limit=limits["max_streams"],
        current_stream_count=0,
        requested_stream_count=stream_count,
        control_message_budget_per_second=config.websocket_limits.control_message_budget_per_second,
        connection_lifetime_hours=config.websocket_limits.max_connection_lifetime_hours,
        reconnect_deadline_utc=compute_reconnect_deadline(now, config),
    )


def validate_control_message_rate(
    config: AppConfig, messages_per_second: int
) -> WebSocketLimitDecision:
    limits = get_ws_limits_for_scope(config)
    allowed = messages_per_second <= config.websocket_limits.control_message_budget_per_second
    now = datetime.now(UTC)
    return WebSocketLimitDecision(
        allowed=allowed,
        reason="Control message rate exceeded" if not allowed else None,
        incoming_message_limit_per_second=limits["max_incoming"],
        stream_limit=limits["max_streams"],
        current_stream_count=0,
        requested_stream_count=0,
        control_message_budget_per_second=config.websocket_limits.control_message_budget_per_second,
        connection_lifetime_hours=config.websocket_limits.max_connection_lifetime_hours,
        reconnect_deadline_utc=compute_reconnect_deadline(now, config),
    )


def compute_reconnect_deadline(started_at_utc: datetime, config: AppConfig) -> datetime:
    lifetime_hours = config.websocket_limits.max_connection_lifetime_hours
    reconnect_before = config.websocket_limits.reconnect_before_disconnect_minutes
    deadline = (
        started_at_utc + timedelta(hours=lifetime_hours) - timedelta(minutes=reconnect_before)
    )
    return deadline


def should_reconnect_now(started_at_utc: datetime, now_utc: datetime, config: AppConfig) -> bool:
    deadline = compute_reconnect_deadline(started_at_utc, config)
    return now_utc >= deadline


def build_websocket_limit_report(config: AppConfig, stream_count: int = 0) -> dict:
    limits = get_ws_limits_for_scope(config)
    return {
        "market_scope": config.runtime.market_scope.value,
        "max_incoming_messages_per_second": limits["max_incoming"],
        "max_streams_per_connection": limits["max_streams"],
        "current_stream_count_request": stream_count,
        "ctrl_msg_budget": config.websocket_limits.control_message_budget_per_second,
        "max_connection_lifetime_hours": config.websocket_limits.max_connection_lifetime_hours,
        "reconn_b4_dc_mins": config.websocket_limits.reconnect_before_disconnect_minutes,
    }
