import pytest
from datetime import datetime, timedelta
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.eligibility import filter_eligible_candidates
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_filter_eligible_candidates_stale():
    config = AppConfig()
    now = datetime.utcnow()

    stale_cand = PortfolioCandidateInput(
        candidate_id="1",
        source_type=CandidateSourceType.scored_signal,
        source_ids=[],
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=now - timedelta(minutes=5), # > 3 bars for 1m
        direction="long",
        signal_score=80.0,
        risk_score=80.0,
        ml_blend_score=80.0,
        source_trace={"a": "b"},
        explanation="Test"
    )

    fresh_cand = PortfolioCandidateInput(
        candidate_id="2",
        source_type=CandidateSourceType.scored_signal,
        source_ids=[],
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=now - timedelta(seconds=30),
        direction="long",
        signal_score=80.0,
        risk_score=80.0,
        ml_blend_score=80.0,
        source_trace={"a": "b"},
        explanation="Test"
    )

    eligible, rejected = filter_eligible_candidates([stale_cand, fresh_cand], config, current_time=now)
    assert len(eligible) == 1
    assert eligible[0].candidate_id == "2"
    assert len(rejected) == 1
    assert rejected[0].candidate_id == "1"
