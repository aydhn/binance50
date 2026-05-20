import random

from pydantic import BaseModel

from binance50.config.models import AppConfig


class BackoffDecision(BaseModel):
    attempt: int
    delay_seconds: float
    max_delay_seconds: float
    jitter_applied: bool
    reason: str | None = None
    status_code: int | None = None
    retryable: bool


def compute_exponential_backoff(
    attempt: int, initial: float, multiplier: float, max_delay: float, jitter: bool = True
) -> float:
    delay = initial * (multiplier**attempt)
    delay = min(delay, max_delay)
    if jitter:
        delay = delay * random.uniform(0.5, 1.0)
    return delay


def is_status_retryable(status_code: int, config: AppConfig) -> bool:
    if status_code == 418:
        return False
    if status_code == 429:
        return config.network.retry_on_429
    if 500 <= status_code < 600:
        return config.network.retry_on_5xx
    return False


def is_exception_retryable(error: Exception, config: AppConfig) -> bool:
    from binance50.core.exceptions import BinanceUnknownExecutionStatusError

    if isinstance(error, BinanceUnknownExecutionStatusError):
        return False

    status_code = getattr(error, "status_code", None)
    if status_code is not None:
        return is_status_retryable(status_code, config)

    return config.network.retry_on_timeout


def compute_retry_delay(
    status_code: int | None, attempt: int, config: AppConfig, retry_after: float | None = None
) -> BackoffDecision:
    if attempt >= config.network.max_retry_attempts:
        return BackoffDecision(
            attempt=attempt,
            delay_seconds=0.0,
            max_delay_seconds=config.network.retry_max_delay_seconds,
            jitter_applied=False,
            reason="Max attempts reached",
            status_code=status_code,
            retryable=False,
        )

    if status_code == 418:
        return BackoffDecision(
            attempt=attempt,
            delay_seconds=0.0,
            max_delay_seconds=config.network.retry_max_delay_seconds,
            jitter_applied=False,
            reason="IP Banned (418)",
            status_code=status_code,
            retryable=False,
        )

    if status_code == 429 and not config.network.retry_on_429:
        delay = retry_after or config.rate_limit.cooldown_on_429_seconds
        return BackoffDecision(
            attempt=attempt,
            delay_seconds=delay,
            max_delay_seconds=config.network.retry_max_delay_seconds,
            jitter_applied=False,
            reason="Rate limit exceeded",
            status_code=status_code,
            retryable=True,
        )

    retryable = True
    if status_code is not None:
        retryable = is_status_retryable(status_code, config)

    if not retryable:
        return BackoffDecision(
            attempt=attempt,
            delay_seconds=0.0,
            max_delay_seconds=config.network.retry_max_delay_seconds,
            jitter_applied=False,
            reason="Not retryable",
            status_code=status_code,
            retryable=False,
        )

    delay = compute_exponential_backoff(
        attempt=attempt,
        initial=config.connector.backoff_initial_seconds,
        multiplier=config.network.retry_multiplier,
        max_delay=config.network.retry_max_delay_seconds,
        jitter=config.network.retry_jitter_enabled,
    )

    if retry_after is not None and retry_after > delay:
        delay = retry_after

    return BackoffDecision(
        attempt=attempt,
        delay_seconds=delay,
        max_delay_seconds=config.network.retry_max_delay_seconds,
        jitter_applied=config.network.retry_jitter_enabled,
        reason="Exponential backoff",
        status_code=status_code,
        retryable=True,
    )
