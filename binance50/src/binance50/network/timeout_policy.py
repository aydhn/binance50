from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigValidationError


class TimeoutPolicy(BaseModel):
    request_timeout_seconds: float
    connect_timeout_seconds: float
    read_timeout_seconds: float
    write_timeout_seconds: float
    pool_timeout_seconds: float


def validate_timeout_policy(policy: TimeoutPolicy) -> None:
    if policy.request_timeout_seconds <= 0:
        raise ConfigValidationError("request_timeout_seconds must be > 0")
    if policy.connect_timeout_seconds <= 0:
        raise ConfigValidationError("connect_timeout_seconds must be > 0")
    if policy.read_timeout_seconds <= 0:
        raise ConfigValidationError("read_timeout_seconds must be > 0")
    if policy.write_timeout_seconds <= 0:
        raise ConfigValidationError("write_timeout_seconds must be > 0")
    if policy.pool_timeout_seconds <= 0:
        raise ConfigValidationError("pool_timeout_seconds must be > 0")


def build_timeout_policy(config: AppConfig) -> TimeoutPolicy:
    policy = TimeoutPolicy(
        request_timeout_seconds=config.network.request_timeout_seconds,
        connect_timeout_seconds=config.network.connect_timeout_seconds,
        read_timeout_seconds=config.network.read_timeout_seconds,
        write_timeout_seconds=config.network.write_timeout_seconds,
        pool_timeout_seconds=config.network.pool_timeout_seconds,
    )
    validate_timeout_policy(policy)
    return policy


def to_httpx_timeout_kwargs(policy: TimeoutPolicy) -> dict:
    import httpx

    timeout = httpx.Timeout(
        policy.request_timeout_seconds,
        connect=policy.connect_timeout_seconds,
        read=policy.read_timeout_seconds,
        write=policy.write_timeout_seconds,
        pool=policy.pool_timeout_seconds,
    )
    return {"timeout": timeout}
