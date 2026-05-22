from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.time_utils import get_utc_now


class StreamConnectionLifecycle(BaseModel):
    connection_id: str
    started_at_utc: datetime
    max_lifetime_hours: int
    reconnect_before_minutes: int
    planned_reconnect_at_utc: datetime
    last_ping_at_utc: datetime | None = None
    last_pong_at_utc: datetime | None = None
    status: str = "active"
    warnings: list[str] = Field(default_factory=list)

def build_stream_lifecycle(config: AppConfig, started_at_utc: datetime | None = None) -> StreamConnectionLifecycle:
    if not started_at_utc:
        started_at_utc = get_utc_now()

    cfg = config.streams.lifecycle
    max_lt = cfg.max_connection_lifetime_hours
    rec_before = cfg.reconnect_before_disconnect_minutes

    planned = started_at_utc + timedelta(hours=max_lt) - timedelta(minutes=rec_before)

    return StreamConnectionLifecycle(
        connection_id=f"conn_{int(started_at_utc.timestamp())}",
        started_at_utc=started_at_utc,
        max_lifetime_hours=max_lt,
        reconnect_before_minutes=rec_before,
        planned_reconnect_at_utc=planned
    )

def should_reconnect(lifecycle: StreamConnectionLifecycle, now_utc: datetime | None = None) -> bool:
    if not now_utc:
        now_utc = get_utc_now()
    return now_utc >= lifecycle.planned_reconnect_at_utc

def record_ping(lifecycle: StreamConnectionLifecycle, now_utc: datetime | None = None) -> StreamConnectionLifecycle:
    if not now_utc:
        now_utc = get_utc_now()
    lifecycle.last_ping_at_utc = now_utc
    return lifecycle

def record_pong(lifecycle: StreamConnectionLifecycle, now_utc: datetime | None = None) -> StreamConnectionLifecycle:
    if not now_utc:
        now_utc = get_utc_now()
    lifecycle.last_pong_at_utc = now_utc
    return lifecycle

def is_pong_timeout(lifecycle: StreamConnectionLifecycle, config: AppConfig, now_utc: datetime | None = None) -> bool:
    if not lifecycle.last_ping_at_utc:
        return False # no ping sent

    if not now_utc:
        now_utc = get_utc_now()

    timeout_sec = config.streams.lifecycle.pong_timeout_seconds

    # if pong received after ping, all good
    if lifecycle.last_pong_at_utc and lifecycle.last_pong_at_utc >= lifecycle.last_ping_at_utc:
        return False

    delta = (now_utc - lifecycle.last_ping_at_utc).total_seconds()
    return delta > timeout_sec
