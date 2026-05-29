import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.concentration import build_concentration_report
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_build_concentration_report():
    config = AppConfig()
    now = datetime.utcnow()
    cands = [
        PortfolioCandidateInput(candidate_id=str(i), source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="BTCUSDT", market_scope="spot", interval="1m", open_time=now, direction="long",
        source_trace={}, explanation="Test") for i in range(5)
    ]

    report = build_concentration_report(cands, config)
    # 5 out of 5 are BTCUSDT, direction long
    assert report.top_3_symbol_weight_pct == 100.0
    assert report.same_direction_ratio == 1.0
    assert len(report.concentration_warnings) > 0
