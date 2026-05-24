from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MarketRegime(StrEnum):
    trend_up = "trend_up"
    trend_down = "trend_down"
    range_bound = "range_bound"
    volatile = "volatile"
    calm = "calm"
    transition = "transition"
    unknown = "unknown"


class RegimeFamily(StrEnum):
    trend = "trend"
    range = "range"
    volatility = "volatility"
    calm = "calm"
    transition = "transition"
    unknown = "unknown"


class RegimeMethod(StrEnum):
    rule_based = "rule_based"
    gmm_optional = "gmm_optional"
    hmm_optional = "hmm_optional"
    hybrid_future = "hybrid_future"


class RegimeStatus(StrEnum):
    valid = "valid"
    warning = "warning"
    invalid = "invalid"
    unknown = "unknown"


class RegimeRiskContext(StrEnum):
    risk_on_candidate = "risk_on_candidate"
    risk_off_candidate = "risk_off_candidate"
    chop_candidate = "chop_candidate"
    breakout_candidate = "breakout_candidate"
    neutral_context = "neutral_context"
    unknown = "unknown"


class RegimeFeatureRow(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    close_time: int
    trend_strength: float | None = None
    trend_slope: float | None = None
    adx_value: float | None = None
    realized_volatility: float | None = None
    realized_volatility_z: float | None = None
    atr_value: float | None = None
    atr_z: float | None = None
    bb_width_pct: float | None = None
    range_score: float | None = None
    volume_z: float | None = None
    signal_confluence_score: float | None = None
    mtf_alignment_score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegimeClassification(BaseModel):
    regime_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    close_time: int
    regime: MarketRegime
    family: RegimeFamily
    method: RegimeMethod
    confidence: float
    stability_score: float | None = None
    risk_context: RegimeRiskContext
    is_transition: bool = False
    explanation: dict[str, Any]
    feature_snapshot: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: int


class RegimeRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    input_dataset_name: str
    method: RegimeMethod
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str
    correlation_id: str | None = None


class RegimeRunMetadata(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    row_count: int
    classification_count: int
    transition_count: int
    input_hash: str
    output_hash: str
    config_hash: str
    method: RegimeMethod
    generated_at_utc: int
    warnings: list[str] = Field(default_factory=list)


class RegimeRunResult(BaseModel):
    request: RegimeRunRequest
    classifications: list[RegimeClassification]
    transitions: list[Any] = Field(default_factory=list)
    quality_report: Any = None
    metadata: RegimeRunMetadata
    success: bool
    error: str | None = None
