import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.ranking import PortfolioCandidateRankingEngine
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_compute_candidate_portfolio_score():
    config = AppConfig()
    engine = PortfolioCandidateRankingEngine(config)
    now = datetime.utcnow()
    cand = PortfolioCandidateInput(
        candidate_id="1", source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="BTC", market_scope="spot", interval="1m", open_time=now, direction="long",
        signal_score=100.0, risk_score=100.0, ml_blend_score=100.0,
        source_trace={}, explanation="Test"
    )

    bd = engine.compute_candidate_portfolio_score(cand, {})
    assert bd.final_portfolio_score <= 100.0 # Clamped
    assert bd.candidate_quality_component > 0
