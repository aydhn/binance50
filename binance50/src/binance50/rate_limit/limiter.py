from collections.abc import Mapping

from binance50.config.models import AppConfig
from binance50.rate_limit.cooldown import CooldownManager
from binance50.rate_limit.models import RateLimitDecision, RateLimitStatus
from binance50.rate_limit.tracker import RateLimitTracker


class RateLimiter:
    def __init__(
        self,
        config: AppConfig,
        tracker: RateLimitTracker | None = None,
        cooldown_manager: CooldownManager | None = None,
    ):
        self.config = config.rate_limit
        self.tracker = tracker or RateLimitTracker(config)
        self.cooldown = cooldown_manager or CooldownManager()

    def check_request_allowed(self, endpoint: str, weight: int = 1) -> RateLimitDecision:
        if self.cooldown.is_active():
            return RateLimitDecision(
                allowed=False,
                hard_stop=self.cooldown._is_hard_stop,
                reason=self.cooldown.get_reason(),
                status=(
                    RateLimitStatus.BANNED
                    if self.cooldown._is_hard_stop
                    else RateLimitStatus.COOLDOWN
                ),
                delay_seconds=self.cooldown.remaining_seconds(),
            )

        status = self.tracker.get_status()
        budgets = self.tracker.get_current_budgets()

        if status == RateLimitStatus.EXCEEDED:
            return RateLimitDecision(
                allowed=False,
                reason="Rate limit budgets exceeded based on estimated usage",
                status=status,
                budgets=budgets,
                delay_seconds=1.0,
            )

        decision = RateLimitDecision(allowed=True, status=status, budgets=budgets)

        if self.config.mode == "conservative" and status in (
            RateLimitStatus.WARNING,
            RateLimitStatus.CRITICAL,
        ):
            decision.should_delay = True
            decision.delay_seconds = 0.5 if status == RateLimitStatus.WARNING else 2.0

        return decision

    def before_request(self, endpoint: str, weight: int = 1) -> RateLimitDecision:
        decision = self.check_request_allowed(endpoint, weight)
        if decision.allowed:
            self.tracker.record_request(weight, endpoint)
        return decision

    def after_response(
        self, endpoint: str, status_code: int, headers: Mapping[str, str]
    ) -> RateLimitDecision:
        decision = self.tracker.record_response(status_code, headers, endpoint)

        if not decision.allowed:
            if status_code == 429:
                delay = decision.retry_after_seconds or self.config.cooldown_on_429_seconds
                self.cooldown.start_cooldown("Rate limit exceeded (429)", delay)
                decision.delay_seconds = delay
            elif status_code == 418:
                delay = decision.retry_after_seconds or self.config.cooldown_on_418_min_seconds
                self.cooldown.start_cooldown("IP Banned (418)", delay, hard=True)
                decision.delay_seconds = delay

        return decision

    def get_required_delay(self, endpoint: str, weight: int = 1) -> float:
        decision = self.check_request_allowed(endpoint, weight)
        if not decision.allowed or decision.should_delay:
            return decision.delay_seconds
        return 0.0

    def force_cooldown(self, seconds: float, reason: str) -> None:
        self.cooldown.start_cooldown(reason, seconds)

    def is_in_cooldown(self) -> bool:
        return self.cooldown.is_active()

    def to_report(self) -> dict:
        return {
            "mode": self.config.mode,
            "tracker": self.tracker.to_report(),
            "cooldown": self.cooldown.to_dict(),
        }
