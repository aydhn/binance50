from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PortfolioConstructionStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    blocked_by_guard = "blocked_by_guard"
    invalid = "invalid"

class PortfolioConstructionIntent(StrEnum):
    research_only = "research_only"
    sandbox_only = "sandbox_only"
    no_order = "no_order"
    no_live = "no_live"
    no_paper = "no_paper"

class PortfolioAllocationMethod(StrEnum):
    equal_weight = "equal_weight"
    inverse_volatility = "inverse_volatility"
    volatility_targeting_skeleton = "volatility_targeting_skeleton"
    risk_parity_skeleton = "risk_parity_skeleton"
    scipy_slsqp_skeleton = "scipy_slsqp_skeleton"
    pyportfolioopt_skeleton = "pyportfolioopt_skeleton"

class PortfolioAllocationStatus(StrEnum):
    sandbox_only = "sandbox_only"
    valid = "valid"
    invalid = "invalid"
    blocked = "blocked"

class PortfolioAllocationItem(BaseModel):
    allocation_item_id: str
    selected_candidate_id: str
    candidate_id: str
    symbol: str
    market_scope: str
    interval: str
    direction: str
    method: PortfolioAllocationMethod
    sandbox_weight: float
    hypothetical_notional_usdt: float
    hypothetical_capital_pct: float
    volatility_estimate_pct: float
    marginal_risk_contribution: float
    component_risk_contribution: float
    percent_risk_contribution: float
    status: PortfolioAllocationStatus = PortfolioAllocationStatus.sandbox_only
    intent: PortfolioConstructionIntent = PortfolioConstructionIntent.sandbox_only
    blocked_from_execution: bool = True
    blocked_from_paper_engine: bool = True
    blocked_from_live_engine: bool = True
    explanation: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class PortfolioAllocationBreakdown(BaseModel):
    method: PortfolioAllocationMethod
    total_weight: float
    cash_buffer_weight: float
    allocated_capital_usdt: float
    expected_portfolio_volatility_pct: float
    concentration_score: float
    max_single_weight_pct: float
    max_symbol_weight_pct: float
    max_pair_correlation: float
    constraint_violations: int = 0
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

class PortfolioConstructionRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    portfolio_selection_run_id: str
    allocation_method: PortfolioAllocationMethod | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str
    correlation_id: str

class PortfolioConstructionRunResult(BaseModel):
    request: PortfolioConstructionRunRequest
    run_id: str
    status: PortfolioConstructionStatus
    selected_candidates: list[Any] = Field(default_factory=list)
    allocation_methods_tested: list[PortfolioAllocationMethod] = Field(default_factory=list)
    allocations_by_method: dict[PortfolioAllocationMethod, list[PortfolioAllocationItem]] = Field(default_factory=dict)
    selected_sandbox_allocation: list[PortfolioAllocationItem] | None = None
    covariance_report: dict[str, Any] | None = None
    volatility_report: dict[str, Any] | None = None
    risk_contribution_report: dict[str, Any] | None = None
    constraint_report: dict[str, Any] | None = None
    optimizer_skeleton_report: dict[str, Any] | None = None
    method_comparison_report: dict[str, Any] | None = None
    quality_report: dict[str, Any] | None = None
    reproducibility_report: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = False
    error: str | None = None
