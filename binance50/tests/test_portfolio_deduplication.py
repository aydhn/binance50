import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.deduplication import deduplicate_candidates
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_deduplicate_candidates_deterministic():
    config = AppConfig()
    now = datetime.utcnow()

    cand1 = PortfolioCandidateInput(
        candidate_id="cand_a",
        source_type=CandidateSourceType.scored_signal,
        source_ids=[],
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=now,
        direction="long",
        signal_score=80.0,
        source_trace={"a": "b"},
        explanation="Test"
    )

    cand2 = PortfolioCandidateInput(
        candidate_id="cand_b",
        source_type=CandidateSourceType.scored_signal,
        source_ids=[],
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=now,
        direction="long",
        signal_score=90.0,
        source_trace={"a": "b"},
        explanation="Test"
    )

    deduped = deduplicate_candidates([cand1, cand2], config)
    assert len(deduped) == 1
    assert deduped[0].candidate_id == "cand_b" # Higher score wins
    assert "cand_a" in deduped[0].metadata["deduplicated_from"]
