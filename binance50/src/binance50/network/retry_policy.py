from binance50.config.models import AppConfig
from binance50.network.backoff import (
    BackoffDecision,
    compute_retry_delay,
    is_exception_retryable,
    is_status_retryable,
)


class RetryController:
    def __init__(self, config: AppConfig):
        self.config = config
        self._attempts = 0

    def should_retry(self, error_or_status, attempt: int) -> bool:
        if attempt >= self.config.network.max_retry_attempts:
            return False

        if isinstance(error_or_status, int):
            return is_status_retryable(error_or_status, self.config)
        elif isinstance(error_or_status, Exception):
            return is_exception_retryable(error_or_status, self.config)

        return False

    def get_delay(
        self, error_or_status, attempt: int, retry_after: float | None = None
    ) -> BackoffDecision:
        status_code = None
        if isinstance(error_or_status, int):
            status_code = error_or_status
        elif hasattr(error_or_status, "status_code"):
            status_code = error_or_status.status_code

        return compute_retry_delay(status_code, attempt, self.config, retry_after)

    def record_attempt(self) -> None:
        self._attempts += 1

    def reset(self) -> None:
        self._attempts = 0
