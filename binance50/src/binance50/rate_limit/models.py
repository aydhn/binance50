from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RateLimitType(StrEnum):
    REQUEST_WEIGHT = "request_weight"
    RAW_REQUESTS = "raw_requests"
    ORDERS = "orders"
    CONNECTIONS = "connections"
    WEBSOCKET_MESSAGES = "websocket_messages"
    UNKNOWN = "unknown"


class RateLimitInterval(StrEnum):
    SECOND = "second"
    MINUTE = "minute"
    FIVE_MINUTES = "five_minutes"
    TEN_SECONDS = "ten_seconds"
    HOUR = "hour"
    DAY = "day"


class RateLimitStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"
    BANNED = "banned"
    COOLDOWN = "cooldown"


class RateLimitHeaderSnapshot(BaseModel):
    used_weight_1m: int | None = None
    used_weight_5m: int | None = None
    used_weight_1h: int | None = None
    raw_requests_5m: int | None = None
    order_count_10s: int | None = None
    order_count_1m: int | None = None
    retry_after_seconds: float | None = None
    ban_until_utc: datetime | None = None
    raw_headers: dict[str, str] = Field(default_factory=dict)
    parsed_at_utc: datetime

    def to_redacted_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        d["raw_headers"] = dict.fromkeys(self.raw_headers.keys(), "***REDACTED***")
        return d


class RateLimitBudget(BaseModel):
    limit_type: RateLimitType
    interval: RateLimitInterval
    limit: int
    used: int
    remaining: int
    usage_pct: float
    status: RateLimitStatus
    reset_hint_utc: datetime | None = None
    source: str = "config"

    def to_redacted_dict(self) -> dict[str, Any]:
        return self.model_dump()


class RateLimitDecision(BaseModel):
    allowed: bool
    should_delay: bool = False
    delay_seconds: float = 0.0
    hard_stop: bool = False
    reason: str | None = None
    status: RateLimitStatus = RateLimitStatus.OK
    budgets: list[RateLimitBudget] = Field(default_factory=list)
    retry_after_seconds: float | None = None
    cooldown_until_utc: datetime | None = None

    def to_redacted_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        d["budgets"] = [b.to_redacted_dict() for b in self.budgets]
        return d


class RateLimitEvent(BaseModel):
    event_id: str
    timestamp_utc: datetime
    event_type: str
    status_code: int | None = None
    endpoint: str | None = None
    weight: int = 1
    decision: RateLimitDecision | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_redacted_dict(self) -> dict[str, Any]:
        d = self.model_dump()
        if self.decision:
            d["decision"] = self.decision.to_redacted_dict()
        if "headers" in d["metadata"]:
            d["metadata"]["headers"] = dict.fromkeys(
                d["metadata"]["headers"].keys(), "***REDACTED***"
            )
        return d
