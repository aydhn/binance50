import time

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigValidationError


class RecvWindowDecision(BaseModel):
    valid: bool
    recv_window_ms: int
    max_recv_window_ms: int
    timestamp_ms: int
    server_time_ms: int
    drift_ms: int
    reason: str | None = None
    warnings: list[str] = Field(default_factory=list)


def validate_recv_window(config: AppConfig, recv_window_ms: int | None = None) -> None:
    rw = recv_window_ms or config.binance_timing.recv_window_ms
    if rw > config.binance_timing.recv_window_max_ms:
        raise ConfigValidationError(
            f"recvWindow {rw} exceeds max {config.binance_timing.recv_window_max_ms}"
        )
    if rw <= 0:
        raise ConfigValidationError("recvWindow must be > 0")


def estimate_safe_recv_window(
    config: AppConfig, observed_latency_ms: float, clock_drift_ms: float
) -> int:
    base = config.binance_timing.recv_window_ms
    estimated = int(base + observed_latency_ms * 2 + abs(clock_drift_ms))
    return min(estimated, config.binance_timing.recv_window_max_ms)


def build_signed_request_timing_params(
    config: AppConfig, local_timestamp_ms: int | None = None
) -> dict:
    ts = local_timestamp_ms or int(time.time() * 1000)
    return {"timestamp": ts, "recvWindow": config.binance_timing.recv_window_ms}


def validate_timestamp_against_server_time(
    timestamp_ms: int, server_time_ms: int, recv_window_ms: int
) -> RecvWindowDecision:
    drift = timestamp_ms - server_time_ms
    valid = True
    reason = None
    warnings = []

    if drift > 1000:
        valid = False
        reason = "Timestamp is too far ahead of server time"

    if server_time_ms - timestamp_ms > recv_window_ms:
        valid = False
        reason = "Timestamp is too old (outside recvWindow)"

    return RecvWindowDecision(
        valid=valid,
        recv_window_ms=recv_window_ms,
        max_recv_window_ms=60000,
        timestamp_ms=timestamp_ms,
        server_time_ms=server_time_ms,
        drift_ms=drift,
        reason=reason,
        warnings=warnings,
    )
