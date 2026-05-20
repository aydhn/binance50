import threading
from datetime import UTC, datetime, timedelta


class CooldownManager:
    def __init__(self):
        self.lock = threading.Lock()
        self._cooldown_until: datetime | None = None
        self._reason: str | None = None
        self._is_hard_stop: bool = False

    def start_cooldown(self, reason: str, seconds: float, hard: bool = False) -> None:
        with self.lock:
            if not self._is_hard_stop or hard:
                self._cooldown_until = datetime.now(UTC) + timedelta(seconds=seconds)
                self._reason = reason
                if hard:
                    self._is_hard_stop = True

    def clear_cooldown(self, reason: str | None = None) -> None:
        with self.lock:
            if reason and self._reason != reason:
                return
            self._cooldown_until = None
            self._reason = None
            self._is_hard_stop = False

    def is_active(self) -> bool:
        with self.lock:
            if not self._cooldown_until:
                return False
            return datetime.now(UTC) < self._cooldown_until

    def remaining_seconds(self) -> float:
        with self.lock:
            if not self._cooldown_until:
                return 0.0
            now = datetime.now(UTC)
            if now >= self._cooldown_until:
                return 0.0
            return (self._cooldown_until - now).total_seconds()

    def get_reason(self) -> str | None:
        with self.lock:
            if not self._cooldown_until or datetime.now(UTC) >= self._cooldown_until:
                return None
            return self._reason

    def to_dict(self) -> dict:
        with self.lock:
            active = self._cooldown_until is not None and datetime.now(UTC) < self._cooldown_until
            return {
                "active": active,
                "reason": self._reason if active else None,
                "remaining_seconds": (
                    (self._cooldown_until - datetime.now(UTC)).total_seconds() if active else 0.0
                ),
                "is_hard_stop": self._is_hard_stop if active else False,
            }
