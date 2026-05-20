import threading
from collections.abc import Mapping
from datetime import UTC, datetime

from binance50.config.models import AppConfig
from binance50.rate_limit.models import (
    RateLimitBudget,
    RateLimitDecision,
    RateLimitHeaderSnapshot,
    RateLimitInterval,
    RateLimitStatus,
    RateLimitType,
)
from binance50.rate_limit.parser import parse_rate_limit_headers


class RateLimitTracker:
    def __init__(self, config: AppConfig):
        self.config = config.rate_limit
        self.lock = threading.Lock()
        self._current_snapshot: RateLimitHeaderSnapshot | None = None
        self._estimated_weight_1m = 0
        self._estimated_orders_10s = 0
        self._estimated_orders_1m = 0
        self._last_update_utc = datetime.now(UTC)
        self._status = RateLimitStatus.OK

    def _reset_estimates_if_needed(self, now: datetime):
        diff = (now - self._last_update_utc).total_seconds()
        if diff > 60:
            self._estimated_weight_1m = 0
            self._estimated_orders_1m = 0
        if diff > 10:
            self._estimated_orders_10s = 0

    def update_from_headers(
        self, headers: Mapping[str, str], endpoint: str | None = None
    ) -> RateLimitHeaderSnapshot:
        snapshot = parse_rate_limit_headers(headers)
        with self.lock:
            self._current_snapshot = snapshot
            if snapshot.used_weight_1m is not None:
                self._estimated_weight_1m = snapshot.used_weight_1m
            if snapshot.order_count_10s is not None:
                self._estimated_orders_10s = snapshot.order_count_10s
            if snapshot.order_count_1m is not None:
                self._estimated_orders_1m = snapshot.order_count_1m
            self._last_update_utc = snapshot.parsed_at_utc
        return snapshot

    def record_request(self, weight: int, endpoint: str | None = None) -> None:
        with self.lock:
            now = datetime.now(UTC)
            self._reset_estimates_if_needed(now)
            self._estimated_weight_1m += weight
            self._last_update_utc = now

    def record_response(
        self, status_code: int, headers: Mapping[str, str], endpoint: str | None = None
    ) -> RateLimitDecision:
        snapshot = self.update_from_headers(headers, endpoint)
        decision = RateLimitDecision(allowed=True)
        if status_code == 429:
            decision.allowed = False
            decision.status = RateLimitStatus.COOLDOWN
            decision.reason = "Rate limit exceeded (429)"
            decision.retry_after_seconds = (
                snapshot.retry_after_seconds or self.config.cooldown_on_429_seconds
            )
        elif status_code == 418:
            decision.allowed = False
            decision.hard_stop = True
            decision.status = RateLimitStatus.BANNED
            decision.reason = "IP Banned (418)"
        return decision

    def _calculate_status(self, usage_pct: float) -> RateLimitStatus:
        if usage_pct >= 100:
            return RateLimitStatus.EXCEEDED
        if usage_pct >= self.config.critical_usage_threshold_pct:
            return RateLimitStatus.CRITICAL
        if usage_pct >= self.config.safety_usage_threshold_pct:
            return RateLimitStatus.WARNING
        return RateLimitStatus.OK

    def get_current_budgets(self) -> list[RateLimitBudget]:
        budgets = []
        with self.lock:
            now = datetime.now(UTC)
            self._reset_estimates_if_needed(now)

            limit_weight = self.config.request_weight_limit_per_minute
            usage_weight_pct = (
                (self._estimated_weight_1m / limit_weight * 100) if limit_weight > 0 else 0
            )
            budgets.append(
                RateLimitBudget(
                    limit_type=RateLimitType.REQUEST_WEIGHT,
                    interval=RateLimitInterval.MINUTE,
                    limit=limit_weight,
                    used=self._estimated_weight_1m,
                    remaining=max(0, limit_weight - self._estimated_weight_1m),
                    usage_pct=usage_weight_pct,
                    status=self._calculate_status(usage_weight_pct),
                )
            )

            limit_orders_10s = self.config.order_count_limit_10s
            usage_orders_10s_pct = (
                (self._estimated_orders_10s / limit_orders_10s * 100) if limit_orders_10s > 0 else 0
            )
            budgets.append(
                RateLimitBudget(
                    limit_type=RateLimitType.ORDERS,
                    interval=RateLimitInterval.TEN_SECONDS,
                    limit=limit_orders_10s,
                    used=self._estimated_orders_10s,
                    remaining=max(0, limit_orders_10s - self._estimated_orders_10s),
                    usage_pct=usage_orders_10s_pct,
                    status=self._calculate_status(usage_orders_10s_pct),
                )
            )

        return budgets

    def get_status(self) -> RateLimitStatus:
        budgets = self.get_current_budgets()
        statuses = [b.status for b in budgets]
        if RateLimitStatus.EXCEEDED in statuses:
            return RateLimitStatus.EXCEEDED
        if RateLimitStatus.CRITICAL in statuses:
            return RateLimitStatus.CRITICAL
        if RateLimitStatus.WARNING in statuses:
            return RateLimitStatus.WARNING
        return RateLimitStatus.OK

    def reset(self) -> None:
        with self.lock:
            self._current_snapshot = None
            self._estimated_weight_1m = 0
            self._estimated_orders_10s = 0
            self._estimated_orders_1m = 0
            self._status = RateLimitStatus.OK
            self._last_update_utc = datetime.now(UTC)

    def to_report(self) -> dict:
        return {
            "status": self.get_status().value,
            "budgets": [b.to_redacted_dict() for b in self.get_current_budgets()],
            "last_update_utc": self._last_update_utc.isoformat(),
        }
