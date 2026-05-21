from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from binance50.core.enums import MarketScope


class OHLCVSource(StrEnum):
    FIXTURE = "fixture"
    CACHE = "cache"
    BINANCE_SPOT_REST = "binance_spot_rest"
    BINANCE_USDM_REST = "binance_usdm_rest"
    MOCK = "mock"


class OHLCVValidationStatus(StrEnum):
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"


class OHLCVGapStatus(StrEnum):
    NO_GAP = "no_gap"
    HAS_GAP = "has_gap"
    UNKNOWN = "unknown"


class OHLCVBar(BaseModel):
    symbol: str
    market_scope: MarketScope
    interval: str
    open_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    close_time: int
    quote_asset_volume: Decimal
    number_of_trades: int
    taker_buy_base_volume: Decimal
    taker_buy_quote_volume: Decimal
    source: OHLCVSource
    is_closed: bool
    raw: list[Any] | None = None

    def dict_redacted(self) -> dict[str, Any]:
        return self.model_dump(exclude={"raw"})


class OHLCVFrameMetadata(BaseModel):
    symbol: str
    market_scope: MarketScope
    interval: str
    source: OHLCVSource
    row_count: int
    start_open_time: int
    end_open_time: int
    generated_at_utc: str
    last_complete_open_time: int | None
    contains_incomplete_last_candle: bool
    cache_path: str | None
    data_hash: str
    quality_status: OHLCVValidationStatus
    warnings: list[str] = Field(default_factory=list)

    def dict_redacted(self) -> dict[str, Any]:
        return self.model_dump()


class OHLCVDataFrame(BaseModel):
    bars: list[OHLCVBar]
    metadata: OHLCVFrameMetadata


class OHLCVFetchPlan(BaseModel):
    plan_id: str
    symbol: str
    market_scope: MarketScope
    interval: str
    requested_start_ms: int
    requested_end_ms: int
    chunks: list["OHLCVFetchChunk"]
    total_expected_requests: int
    max_limit: int
    endpoint_path: str
    estimated_weight: int
    created_at_utc: str
    warnings: list[str] = Field(default_factory=list)


class OHLCVFetchChunk(BaseModel):
    chunk_id: str
    symbol: str
    interval: str
    start_time_ms: int
    end_time_ms: int
    limit: int
    endpoint_path: str
    estimated_weight: int
    reason: str


class OHLCVFetchRequest(BaseModel):
    symbol: str
    market_scope: MarketScope
    interval: str
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    limit: int | None = None
    source: OHLCVSource
    request_id: str
    correlation_id: str

    def dict_redacted(self) -> dict[str, Any]:
        return self.model_dump()


class OHLCVFetchResult(BaseModel):
    request: OHLCVFetchRequest
    bars: list[OHLCVBar]
    response_metadata: dict[str, Any]
    rate_limit_metadata: dict[str, Any]
    success: bool
    error: str | None = None
    fetched_at_utc: str

    def dict_redacted(self) -> dict[str, Any]:
        d = self.model_dump(exclude={"bars", "response_metadata"})
        d["bar_count"] = len(self.bars)
        return d
