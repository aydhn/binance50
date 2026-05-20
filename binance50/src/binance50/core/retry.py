from pydantic import BaseModel, Field

from binance50.config.models import AppConfig


class RetryPolicy(BaseModel):
    max_attempts: int
    initial_delay_seconds: float
    max_delay_seconds: float
    multiplier: float = 2.0
    jitter_enabled: bool = True
    retry_on_status_codes: list[int] = Field(default_factory=lambda: [429, 418, 500, 502, 503, 504])
    retry_on_error_codes: list[int] = Field(default_factory=list)


def build_retry_policy(config: AppConfig) -> RetryPolicy:
    return RetryPolicy(
        max_attempts=config.connector.max_retry_attempts,
        initial_delay_seconds=config.connector.backoff_initial_seconds,
        max_delay_seconds=config.connector.backoff_max_seconds,
    )


def compute_backoff_delay(attempt: int, policy: RetryPolicy) -> float:
    if attempt >= policy.max_attempts:
        return 0.0
    delay = policy.initial_delay_seconds * (policy.multiplier**attempt)
    return min(delay, policy.max_delay_seconds)


def should_retry_status(status_code: int, policy: RetryPolicy) -> bool:
    return status_code in policy.retry_on_status_codes


def should_retry_exception(error: Exception, policy: RetryPolicy) -> bool:
    # Note on 5XX and execution status metadata
    from binance50.core.exceptions import BinanceUnknownExecutionStatusError

    if isinstance(error, BinanceUnknownExecutionStatusError):
        # We don't generally retry unknown execution statuses as it's unsafe without query
        return False
    # If the exception has a status_code attr, we might check it
    if hasattr(error, "status_code"):
        return should_retry_status(error.status_code, policy)
    return False
