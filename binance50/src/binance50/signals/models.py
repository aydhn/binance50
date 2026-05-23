import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from binance50.strategies.models import SignalCandidate


class ScoredSignalStatus(StrEnum):
    scored_candidate = "scored_candidate"
    rejected = "rejected"
    warning = "warning"
    no_action = "no_action"
    conflicted = "conflicted"
    expired = "expired"


class SignalScoreTier(StrEnum):
    very_low = "very_low"
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very_high"


class SignalDecisionIntent(StrEnum):
    research_candidate = "research_candidate"
    risk_review_candidate = "risk_review_candidate"
    future_backtest_candidate = "future_backtest_candidate"
    no_action = "no_action"
    no_order = "no_order"


class SignalScoreComponentName(StrEnum):
    candidate_confidence = "candidate_confidence"
    plugin_weighted_score = "plugin_weighted_score"
    confluence = "confluence"
    confirmation = "confirmation"
    freshness = "freshness"
    data_quality = "data_quality"
    conflict_penalty = "conflict_penalty"


class SignalScoreComponent(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    raw_value: float
    normalized_value: float
    weight: float
    contribution: float
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SignalScoreBreakdown(BaseModel):
    model_config = ConfigDict(frozen=True)

    components: list[SignalScoreComponent] = Field(default_factory=list)
    subtotal_before_penalties: float
    total_penalty: float
    final_score: float
    score_tier: SignalScoreTier
    warnings: list[str] = Field(default_factory=list)


class ConfluenceGroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    group_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: datetime.datetime | int
    direction: str
    candidates: list[SignalCandidate] = Field(default_factory=list)
    plugin_names: list[str] = Field(default_factory=list)
    plugin_types: list[str] = Field(default_factory=list)
    same_direction_count: int
    opposite_direction_count: int
    confluence_score: float
    conflict_penalty: float
    warnings: list[str] = Field(default_factory=list)


class ScoredSignalCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    scored_signal_id: str
    source_candidate_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: datetime.datetime | int
    close_time: datetime.datetime | int | None = None
    direction: str
    status: ScoredSignalStatus
    intent: SignalDecisionIntent
    score: float = Field(ge=0.0, le=100.0)
    score_tier: SignalScoreTier
    confidence: float
    plugin_name: str
    plugin_type: str
    strategy_strength: str
    score_breakdown: SignalScoreBreakdown | None = None
    confluence_group_id: str | None = None
    conflicted: bool = False
    conflict_reasons: list[str] = Field(default_factory=list)
    expired: bool = False
    explanation: str | None = None
    source_candidate: SignalCandidate | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: datetime.datetime | int | None = None


class SignalScoringRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    market_scope: str
    interval: str
    candidate_dataset_name: str = "strategy_candidates"
    plugin_names: list[str] | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str | None = None
    correlation_id: str | None = None


class SignalScoringMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    market_scope: str
    interval: str
    input_candidate_count: int
    scored_candidate_count: int
    rejected_candidate_count: int
    confluence_group_count: int
    conflict_count: int
    input_hash: str
    output_hash: str
    config_hash: str
    generated_at_utc: datetime.datetime | int
    warnings: list[str] = Field(default_factory=list)


class SignalScoringResult(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    request: SignalScoringRequest
    scored_candidates: list[ScoredSignalCandidate] = Field(default_factory=list)
    rejected_candidates: list[ScoredSignalCandidate] = Field(default_factory=list)
    confluence_groups: list[ConfluenceGroup] = Field(default_factory=list)
    quality_report: Any | None = None
    metadata: SignalScoringMetadata
    success: bool
    error: str | None = None
