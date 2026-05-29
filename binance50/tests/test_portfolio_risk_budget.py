import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.risk_budget import compute_total_risk_budget
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_compute_total_risk_budget():
    config = AppConfig()
    now = datetime.utcnow()
    cands = [
        PortfolioCandidateInput(candidate_id="1", source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="BTC", market_scope="spot", interval="1m", open_time=now, direction="long",
        source_trace={}, explanation="Test")
    ]

    report = compute_total_risk_budget(cands, config)
    assert report.total_hypothetical_risk_budget_pct > 0.0
