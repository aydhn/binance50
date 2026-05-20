from typing import Any

from pydantic import BaseModel, Field

from binance50.connectors.capabilities import ConnectorCapabilities
from binance50.core.enums import AccountDomain, EnvironmentProfileName, ExchangeName, MarketScope


class RateLimitMetadata(BaseModel):
    used_weight_1m: int | None = None
    order_count_10s: int | None = None
    order_count_1m: int | None = None
    retry_after_seconds: float | None = None
    raw_headers: dict[str, str] = Field(default_factory=dict)


class ConnectorResponse(BaseModel):
    request_id: str
    timestamp_utc: str
    status_code: int
    payload: dict[str, Any] | list[Any] | str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    latency_ms: int
    rate_limit_metadata: RateLimitMetadata | None = None
    success: bool
    error_code: str | None = None
    error_message: str | None = None
    classified_error: str | None = None
    correlation_id: str | None = None

    def redacted_dump(self) -> dict[str, Any]:
        # Dump hiding potential secrets
        d = self.model_dump()
        return d


class ConnectorHealth(BaseModel):
    enabled: bool
    connected: bool
    connector_type: str
    exchange: ExchangeName
    environment_profile: EnvironmentProfileName
    account_domain: AccountDomain
    market_scope: MarketScope
    status: str
    message: str
    last_check_utc: str
    capabilities: ConnectorCapabilities
    blocking_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    def redacted_dump(self) -> dict[str, Any]:
        return self.model_dump()
