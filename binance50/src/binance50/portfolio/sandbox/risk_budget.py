from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioRiskBudgetReport(BaseModel):
    run_id: str
    total_hypothetical_risk_budget_pct: float
    risk_budget_by_candidate: dict[str, float] = Field(default_factory=dict)
    risk_budget_by_symbol: dict[str, float] = Field(default_factory=dict)
    risk_budget_violations: list[str] = Field(default_factory=list)
    budget_is_hypothetical: bool = True
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


def estimate_candidate_risk_budget(candidate: PortfolioCandidateInput, config: AppConfig) -> float:
    # Hypothetical placeholder calculation
    b_config = config.portfolio_sandbox.risk_budget
    return b_config.max_single_candidate_risk_budget_pct * 0.5


def check_single_candidate_budget(budget_pct: float, config: AppConfig) -> tuple[bool, str | None]:
    limit = config.portfolio_sandbox.risk_budget.max_single_candidate_risk_budget_pct
    if budget_pct > limit:
        return False, f"Candidate risk budget {budget_pct}% exceeds limit {limit}%"
    return True, None


def check_total_budget(total_pct: float, config: AppConfig) -> tuple[bool, str | None]:
    limit = config.portfolio_sandbox.risk_budget.max_total_risk_budget_pct
    if total_pct > limit:
        return False, f"Total risk budget {total_pct}% exceeds limit {limit}%"
    return True, None


def compute_total_risk_budget(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioRiskBudgetReport:
    b_config = config.portfolio_sandbox.risk_budget

    report = PortfolioRiskBudgetReport(run_id="unknown", total_hypothetical_risk_budget_pct=0.0)

    if not b_config.enabled:
        return report

    for cand in candidates:
        budget = estimate_candidate_risk_budget(cand, config)
        report.risk_budget_by_candidate[cand.candidate_id] = budget
        report.risk_budget_by_symbol[cand.symbol] = (
            report.risk_budget_by_symbol.get(cand.symbol, 0.0) + budget
        )
        report.total_hypothetical_risk_budget_pct += budget

        ok, msg = check_single_candidate_budget(budget, config)
        if not ok:
            report.risk_budget_violations.append(f"Candidate {cand.candidate_id}: {msg}")

    ok, msg = check_total_budget(report.total_hypothetical_risk_budget_pct, config)
    if not ok:
        report.risk_budget_violations.append(msg)

    return report


def build_risk_budget_report(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioRiskBudgetReport:
    return compute_total_risk_budget(candidates, config)
