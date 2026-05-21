from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from binance50.core.enums import MarketScope


class SymbolStatus(StrEnum):
    TRADING = "trading"
    HALT = "halt"
    BREAK_STATUS = "break_status"
    UNKNOWN = "unknown"


class SymbolRejectionReason(StrEnum):
    NOT_TRADING = "not_trading"
    QUOTE_ASSET_NOT_ALLOWED = "quote_asset_not_allowed"
    BLACKLISTED = "blacklisted"
    STABLECOIN_PAIR = "stablecoin_pair"
    LEVERAGED_TOKEN = "leveraged_token"
    FAN_TOKEN = "fan_token"
    MISSING_FILTERS = "missing_filters"
    MISSING_24H_TICKER = "missing_24h_ticker"
    MISSING_BOOK_TICKER = "missing_book_ticker"
    LOW_QUOTE_VOLUME = "low_quote_volume"
    LOW_TRADE_COUNT = "low_trade_count"
    HIGH_SPREAD = "high_spread"
    LOW_BID_ASK_DEPTH = "low_bid_ask_depth"
    MIN_NOTIONAL_TOO_HIGH = "min_notional_too_high"
    BAD_PRICE_TICK = "bad_price_tick"
    BAD_QTY_STEP = "bad_qty_step"
    UNSUPPORTED_MARKET_SCOPE = "unsupported_market_scope"
    INSUFFICIENT_METADATA = "insufficient_metadata"
    SCORE_BELOW_THRESHOLD = "score_below_threshold"


class SymbolDecisionStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WARNING = "warning"


class SymbolFilterType(StrEnum):
    PRICE_FILTER = "price_filter"
    LOT_SIZE = "lot_size"
    MARKET_LOT_SIZE = "market_lot_size"
    MIN_NOTIONAL = "min_notional"
    NOTIONAL = "notional"
    PERCENT_PRICE = "percent_price"
    PERCENT_PRICE_BY_SIDE = "percent_price_by_side"
    ICEBERG_PARTS = "iceberg_parts"
    MAX_NUM_ORDERS = "max_num_orders"
    MAX_NUM_ALGO_ORDERS = "max_num_algo_orders"
    UNKNOWN = "unknown"


class SymbolFilter(BaseModel):
    filter_type: SymbolFilterType
    raw: dict[str, Any]
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    tick_size: Decimal | None = None
    min_qty: Decimal | None = None
    max_qty: Decimal | None = None
    step_size: Decimal | None = None
    min_notional: Decimal | None = None
    max_notional: Decimal | None = None
    apply_to_market: bool | None = None
    avg_price_mins: int | None = None


class SymbolMetadata(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    status: SymbolStatus
    market_scope: MarketScope
    permissions: list[str] = Field(default_factory=list)
    contract_type: str | None = None
    margin_asset: str | None = None
    filters: dict[SymbolFilterType, SymbolFilter] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class Ticker24h(BaseModel):
    symbol: str
    price_change_percent: Decimal
    last_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    trade_count: int
    raw: dict[str, Any] = Field(default_factory=dict)


class BookTicker(BaseModel):
    symbol: str
    bid_price: Decimal
    bid_qty: Decimal
    ask_price: Decimal
    ask_qty: Decimal
    raw: dict[str, Any] = Field(default_factory=dict)


class SpreadMetrics(BaseModel):
    symbol: str
    bid: Decimal
    ask: Decimal
    mid: Decimal
    spread_abs: Decimal
    spread_bps: Decimal
    valid: bool


class LiquidityMetrics(BaseModel):
    symbol: str
    quote_volume_24h: Decimal
    base_volume_24h: Decimal
    trade_count_24h: int
    bid_notional: Decimal
    ask_notional: Decimal
    depth_notional: Decimal
    valid: bool


class SymbolRuleQuality(BaseModel):
    symbol: str
    has_price_filter: bool
    has_lot_size: bool
    has_min_notional: bool
    min_notional: Decimal | None = None
    tick_size: Decimal | None = None
    step_size: Decimal | None = None
    price_tick_pct: Decimal | None = None
    qty_step_pct: Decimal | None = None
    quality_score: float
    warnings: list[str] = Field(default_factory=list)


class UniverseCandidate(BaseModel):
    symbol: str
    market_scope: MarketScope
    metadata: SymbolMetadata
    ticker_24h: Ticker24h | None = None
    book_ticker: BookTicker | None = None
    spread: SpreadMetrics | None = None
    liquidity: LiquidityMetrics | None = None
    rule_quality: SymbolRuleQuality | None = None
    score: float = 0.0
    decision_status: SymbolDecisionStatus = SymbolDecisionStatus.WARNING
    rejection_reasons: list[SymbolRejectionReason] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class UniverseSelectionResult(BaseModel):
    selected_symbols: list[str] = Field(default_factory=list)
    rejected_symbols: list[str] = Field(default_factory=list)
    candidates: dict[str, UniverseCandidate] = Field(default_factory=dict)
    generated_at_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))
    config_summary: dict[str, Any] = Field(default_factory=dict)
    source_snapshot_id: str | None = None
    report: dict[str, Any] = Field(default_factory=dict)
