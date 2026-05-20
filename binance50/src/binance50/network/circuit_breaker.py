import threading
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from binance50.config.models import AppConfig


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, config: AppConfig):
        self.config = config.network
        self.lock = threading.Lock()
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._open_until: datetime | None = None

    def record_success(self) -> None:
        with self.lock:
            self._failures = 0
            self._state = CircuitState.CLOSED
            self._open_until = None

    def record_failure(self, reason: str, status_code: int | None = None) -> None:
        with self.lock:
            if status_code == 418:
                self._failures = self.config.circuit_breaker_failure_threshold
            else:
                self._failures += 1

            if self._failures >= self.config.circuit_breaker_failure_threshold:
                self._state = CircuitState.OPEN
                self._open_until = datetime.now(UTC) + timedelta(
                    seconds=self.config.circuit_breaker_cooldown_seconds
                )

    def allow_request(self) -> bool:
        if not self.config.circuit_breaker_enabled:
            return True

        with self.lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                if self._open_until and datetime.now(UTC) > self._open_until:
                    self._state = CircuitState.HALF_OPEN
                    return True
                return False

            return self._state == CircuitState.HALF_OPEN

    def maybe_half_open(self) -> CircuitState:
        with self.lock:
            if (
                self._state == CircuitState.OPEN
                and self._open_until
                and datetime.now(UTC) > self._open_until
            ):
                self._state = CircuitState.HALF_OPEN
            return self._state

    def reset(self) -> None:
        with self.lock:
            self._state = CircuitState.CLOSED
            self._failures = 0
            self._open_until = None

    def to_report(self) -> dict:
        with self.lock:
            return {
                "enabled": self.config.circuit_breaker_enabled,
                "state": self._state.value,
                "failures": self._failures,
                "open_until": self._open_until.isoformat() if self._open_until else None,
            }
