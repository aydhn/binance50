import pytest
from datetime import datetime
from binance50.portfolio.sandbox.models import PortfolioSelectedSandboxCandidate, PortfolioSandboxIntent, PortfolioCandidateStatus, PortfolioCandidateScoreBreakdown

def test_selected_sandbox_candidate_defaults():
    breakdown = PortfolioCandidateScoreBreakdown(
        candidate_quality_component=10.0,
        risk_quality_component=10.0,
        ml_blend_component=10.0,
        diversification_component=0.0,
        correlation_penalty=0.0,
        concentration_penalty=0.0,
        liquidity_penalty=0.0,
        stale_candidate_penalty=0.0,
        final_portfolio_score=30.0
    )

    candidate = PortfolioSelectedSandboxCandidate(
        selected_id="sel_1",
        candidate_id="cand_1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        direction="long",
        rank=1,
        selected=True,
        status=PortfolioCandidateStatus.selected_sandbox,
        intent=PortfolioSandboxIntent.sandbox_only,
        portfolio_score=30.0,
        score_breakdown=breakdown,
        hypothetical_notional_usdt=50.0,
        hypothetical_exposure_pct=5.0,
        hypothetical_risk_budget_pct=1.0,
        explanation="Test explanation",
        created_at_utc=datetime.utcnow()
    )

    assert candidate.blocked_from_execution is True
    assert candidate.blocked_from_live_engine is True
    assert candidate.blocked_from_paper_engine is True
    assert candidate.blocked_from_risk_engine is True
    assert candidate.blocked_from_signal_engine is True
