import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.exposure import compute_total_exposure
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_compute_total_exposure_violations():
    config = AppConfig()
    config.portfolio_sandbox.exposure.max_total_hypothetical_exposure_pct = 5.0
    config.portfolio_sandbox.exposure.default_candidate_notional_usdt = 100.0
    config.portfolio_sandbox.exposure.starting_equity_usdt = 1000.0

    cand = PortfolioCandidateInput(
        candidate_id="1", source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="BTCUSDT", market_scope="spot", interval="1m", open_time=datetime.utcnow(), direction="long",
        source_trace={}, explanation="Test"
    )

    report = compute_total_exposure([cand], config)
    # 100 / 1000 = 10% exposure > 5% limit
    assert len(report.violations) > 0
    assert "exceeds limit (5.0%)" in report.violations[0]
