import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrategyDirection(StrEnum):
    bullish = "bullish"
    bearish = "bearish"
    neutral = "neutral"
    no_action = "no_action"


class StrategyCandidateStrength(StrEnum):
    weak = "weak"
    medium = "medium"
    strong = "strong"


class StrategyCandidateStatus(StrEnum):
    candidate = "candidate"
    rejected = "rejected"
    warning = "warning"
    no_action = "no_action"


class StrategyPluginType(StrEnum):
    trend_following = "trend_following"
    mean_reversion = "mean_reversion"
    momentum_continuation = "momentum_continuation"
    volatility_breakout = "volatility_breakout"
    volume_confirmation = "volume_confirmation"
    divergence_candidate = "divergence_candidate"
    mtf_confirmation = "mtf_confirmation"
    pattern_candidate = "pattern_candidate"
    composite_skeleton = "composite_skeleton"


class StrategyIntent(StrEnum):
    research_candidate = "research_candidate"
    explanation_only = "explanation_only"
    scoring_input = "scoring_input"
    no_order = "no_order"


class StrategyRejectionReason(StrEnum):
    missing_required_feature = "missing_required_feature"
    insufficient_history = "insufficient_history"
    warmup_row = "warmup_row"
    invalid_feature_value = "invalid_feature_value"
    condition_not_met = "condition_not_met"
    conflicting_conditions = "conflicting_conditions"
    confidence_out_of_range = "confidence_out_of_range"
    missing_explanation = "missing_explanation"
    order_language_detected = "order_language_detected"
    unsafe_input = "unsafe_input"
    plugin_error = "plugin_error"


class StrategyConditionEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    feature_name: str
    operator: str
    threshold: float | str | None = None
    actual_value: float | str | None = None
    passed: bool
    weight: float = 1.0
    message: str | None = None


class StrategyExplanation(BaseModel):
    model_config = ConfigDict(frozen=True)

    summary: str
    evidence: list[StrategyConditionEvidence] = Field(default_factory=list)
    passed_conditions: list[str] = Field(default_factory=list)
    failed_conditions: list[str] = Field(default_factory=list)
    feature_snapshot: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    human_readable: str = ""
    machine_readable: dict[str, Any] = Field(default_factory=dict)


class SignalCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: datetime.datetime | int
    close_time: datetime.datetime | int | None = None
    plugin_name: str
    plugin_type: StrategyPluginType
    direction: StrategyDirection
    strength: StrategyCandidateStrength
    confidence: float = Field(ge=0.0, le=100.0)
    status: StrategyCandidateStatus = StrategyCandidateStatus.candidate
    intent: StrategyIntent = StrategyIntent.no_order
    expiry_bars: int = 3
    explanation: StrategyExplanation
    required_features: list[str] = Field(default_factory=list)
    used_features: list[str] = Field(default_factory=list)
    rejection_reasons: list[StrategyRejectionReason] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: datetime.datetime | int | None = None


class StrategyRunRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    market_scope: str
    interval: str
    input_dataset_name: str = "indicator_features_v2"
    plugin_names: list[str] | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str | None = None
    correlation_id: str | None = None


class StrategyRunMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    market_scope: str
    interval: str
    row_count: int
    plugin_count: int
    candidate_count: int
    rejected_count: int
    input_hash: str
    output_hash: str
    config_hash: str
    generated_at_utc: datetime.datetime | int
    warnings: list[str] = Field(default_factory=list)


class StrategyRunResult(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    request: StrategyRunRequest
    candidates: list[SignalCandidate] = Field(default_factory=list)
    rejected_candidates: list[SignalCandidate] = Field(default_factory=list)
    plugin_reports: dict[str, Any] = Field(default_factory=dict)
    quality_report: Any | None = None
    metadata: StrategyRunMetadata
    success: bool
    error: str | None = None
