from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PortfolioSandboxStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    blocked_by_guard = "blocked_by_guard"
    invalid = "invalid"


class PortfolioSandboxIntent(str, Enum):
    research_only = "research_only"
    sandbox_only = "sandbox_only"
    no_order = "no_order"
    no_live = "no_live"
    no_paper = "no_paper"


class CandidateSourceType(str, Enum):
    scored_signal = "scored_signal"
    risk_assessment = "risk_assessment"
    ml_blended_candidate = "ml_blended_candidate"
    combined = "combined"


class PortfolioCandidateStatus(str, Enum):
    eligible = "eligible"
    rejected = "rejected"
    penalized = "penalized"
    selected_sandbox = "selected_sandbox"
    blocked = "blocked"


class PortfolioCandidateInput(BaseModel):
    candidate_id: str
    source_type: CandidateSourceType
    source_ids: list[str]
    symbol: str
    market_scope: str
    interval: str
    open_time: datetime
    close_time: datetime | None = None
    direction: str
    signal_score: float | None = None
    risk_score: float | None = None
    ml_blend_score: float | None = None
    regime: str | None = None
    risk_context: dict | None = None
    hypothetical_notional_usdt: float | None = None
    source_trace: dict
    explanation: str
    metadata: dict = Field(default_factory=dict)


class PortfolioCandidateScoreBreakdown(BaseModel):
    candidate_quality_component: float
    risk_quality_component: float
    ml_blend_component: float
    diversification_component: float
    correlation_penalty: float
    concentration_penalty: float
    liquidity_penalty: float
    stale_candidate_penalty: float
    final_portfolio_score: float
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class PortfolioSelectedSandboxCandidate(BaseModel):
    selected_id: str
    candidate_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: datetime
    direction: str
    rank: int
    selected: bool
    status: PortfolioCandidateStatus
    intent: PortfolioSandboxIntent
    blocked_from_signal_engine: bool = True
    blocked_from_risk_engine: bool = True
    blocked_from_paper_engine: bool = True
    blocked_from_live_engine: bool = True
    blocked_from_execution: bool = True
    portfolio_score: float
    score_breakdown: PortfolioCandidateScoreBreakdown
    hypothetical_notional_usdt: float
    hypothetical_exposure_pct: float
    hypothetical_risk_budget_pct: float
    explanation: str
    metadata: dict = Field(default_factory=dict)
    created_at_utc: datetime


class PortfolioSelectionRunRequest(BaseModel):
    symbol: str | None = None
    market_scope: str | None = None
    interval: str | None = None
    scored_signal_run_id: str | None = None
    risk_run_id: str | None = None
    ml_blending_run_id: str | None = None
    regime_run_id: str | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str | None = None
    correlation_id: str | None = None


class PortfolioSelectionRunResult(BaseModel):
    request: PortfolioSelectionRunRequest
    run_id: str
    status: PortfolioSandboxStatus
    input_candidates: list[PortfolioCandidateInput] = Field(default_factory=list)
    eligible_candidates: list[PortfolioCandidateInput] = Field(default_factory=list)
    rejected_candidates: list[PortfolioCandidateInput] = Field(default_factory=list)
    selected_candidates: list[PortfolioSelectedSandboxCandidate] = Field(default_factory=list)
    correlation_report: dict | None = None
    similarity_report: dict | None = None
    exposure_report: dict | None = None
    concentration_report: dict | None = None
    diversification_report: dict | None = None
    risk_budget_report: dict | None = None
    optimizer_skeleton_report: dict | None = None
    quality_report: dict | None = None
    reproducibility_report: dict | None = None
    metadata: dict = Field(default_factory=dict)
    success: bool = False
    error: str | None = None
