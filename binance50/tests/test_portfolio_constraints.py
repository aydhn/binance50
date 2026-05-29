import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.constraints import check_max_candidates
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_check_max_candidates():
    config = AppConfig()
    config.portfolio_sandbox.exposure.max_candidates_selected = 1
    now = datetime.utcnow()
    cands = [
        PortfolioCandidateInput(candidate_id=str(i), source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="BTC", market_scope="spot", interval="1m", open_time=now, direction="long",
        source_trace={}, explanation="Test") for i in range(2)
    ]

    res = check_max_candidates(cands, config)
    assert res.passed is False
    assert res.severity == "block"
