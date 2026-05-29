import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.selection import select_top_candidates
from binance50.portfolio.sandbox.models import PortfolioSelectedSandboxCandidate, PortfolioSandboxIntent, PortfolioCandidateStatus

def test_select_top_candidates_marks_non_selected():
    config = AppConfig()
    config.portfolio_sandbox.exposure.max_candidates_selected = 1
    now = datetime.utcnow()

    cands = [
        PortfolioSelectedSandboxCandidate(
            selected_id=f"sel_{i}", candidate_id=str(i), symbol="BTC", market_scope="spot", interval="1m",
            open_time=now, direction="long", rank=0, selected=False, status=PortfolioCandidateStatus.eligible,
            intent=PortfolioSandboxIntent.sandbox_only, portfolio_score=100.0 - i,
            score_breakdown={"final_portfolio_score": 100.0 - i, "candidate_quality_component": 0, "risk_quality_component": 0, "ml_blend_component": 0, "diversification_component": 0, "correlation_penalty": 0, "concentration_penalty": 0, "liquidity_penalty": 0, "stale_candidate_penalty": 0, "warnings": [], "metadata": {}},
            hypothetical_notional_usdt=0, hypothetical_exposure_pct=0, hypothetical_risk_budget_pct=0,
            explanation="Test", created_at_utc=now
        ) for i in range(2)
    ]

    selected = select_top_candidates(cands, config)
    assert len(selected) == 1
    assert cands[0].selected is True
    assert cands[1].selected is False
    assert cands[1].status == PortfolioCandidateStatus.rejected
