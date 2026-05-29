import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.diversification import build_diversification_report
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_build_diversification_report():
    config = AppConfig()
    now = datetime.utcnow()
    cands = [
        PortfolioCandidateInput(candidate_id=str(i), source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol=f"SYM{i}", market_scope="spot", interval="1m", open_time=now, direction="long",
        source_trace={}, explanation="Test") for i in range(5)
    ]

    report = build_diversification_report(cands, None, config)
    assert report.symbol_diversity_score == 1.0
