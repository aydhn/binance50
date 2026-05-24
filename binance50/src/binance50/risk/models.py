from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class RiskAssessmentStatus(str, Enum):
    approved_for_future_backtest = "approved_for_future_backtest"
    approved_for_paper_review = "approved_for_paper_review"
    needs_review = "needs_review"
    rejected_by_risk = "rejected_by_risk"
    blocked_by_policy = "blocked_by_policy"
    no_action = "no_action"


class RiskIntent(str, Enum):
    no_order = "no_order"
    risk_review = "risk_review"
    simulation_only = "simulation_only"
    future_backtest_candidate = "future_backtest_candidate"
    paper_review_candidate = "paper_review_candidate"


class RiskDimension(str, Enum):
    signal_score = "signal_score"
    regime = "regime"
    volatility = "volatility"
    liquidity = "liquidity"
    conflict = "conflict"
    data_quality = "data_quality"
    notional = "notional"
    symbol_filter = "symbol_filter"
    leverage = "leverage"
    exposure = "exposure"
    drawdown = "drawdown"
    frequency = "frequency"
    operational = "operational"


class RiskSeverity(str, Enum):
    info = "info"
    warning = "warning"
    high = "high"
    critical = "critical"
    blocked = "blocked"


class RiskComponent(BaseModel):
    dimension: RiskDimension
    raw_value: float | None = None
    normalized_risk: float = 0.0
    penalty: float = 0.0
    bonus: float = 0.0
    passed: bool = True
    severity: RiskSeverity = RiskSeverity.info
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskBreakdown(BaseModel):
    components: list[RiskComponent] = Field(default_factory=list)
    base_score: float = 0.0
    total_penalty: float = 0.0
    total_bonus: float = 0.0
    final_risk_score: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    assessment_id: str
    source_scored_signal_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: datetime
    close_time: datetime
    direction: str
    status: RiskAssessmentStatus
    intent: RiskIntent
    final_risk_score: float
    risk_tier: str
    approved: bool
    blocked: bool
    needs_review: bool
    breakdown: RiskBreakdown
    explanation: str
    regime_context: dict[str, Any] | None = None
    signal_snapshot: dict[str, Any] | None = None
    hypothetical_notional_usdt: float | None = None
    hypothetical_risk_pct: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_no_execution_fields(self) -> "RiskAssessment":
        forbidden_fields = [
            "order_id",
            "qty",
            "quantity",
            "leverage_to_set",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
            "order_type",
            "side",
            "reduce_only",
            "position_side",
        ]
        for field in forbidden_fields:
            if hasattr(self, field):
                raise ValueError(f"Execution field '{field}' is forbidden in RiskAssessment")
            if field in self.metadata:
                raise ValueError(f"Execution field '{field}' is forbidden in metadata")
        return self


class RiskRunRequest(BaseModel):
    symbol: str | None = None
    market_scope: str | None = None
    interval: str | None = None
    input_signal_dataset_name: str | None = None
    input_regime_dataset_name: str | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str | None = None
    correlation_id: str | None = None


class RiskQualityIssue(BaseModel):
    issue_type: str
    severity: str
    assessment_id: str | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskQualityReport(BaseModel):
    status: str
    assessment_count: int = 0
    rejected_count: int = 0
    blocked_count: int = 0
    needs_review_count: int = 0
    approved_future_backtest_count: int = 0
    approved_paper_review_count: int = 0
    missing_explanation_count: int = 0
    missing_breakdown_count: int = 0
    execution_field_count: int = 0
    order_language_count: int = 0
    score_out_of_range_count: int = 0
    issues: list[RiskQualityIssue] = Field(default_factory=list)
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)


class RiskRunResult(BaseModel):
    request: RiskRunRequest
    assessments: list[RiskAssessment] = Field(default_factory=list)
    rejected_assessments: list[RiskAssessment] = Field(default_factory=list)
    quality_report: RiskQualityReport | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: str | None = None
