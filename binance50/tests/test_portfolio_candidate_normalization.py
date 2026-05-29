import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.normalization import normalize_candidate_scores
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_normalize_candidate_scores():
    config = AppConfig()
    candidates = [
        PortfolioCandidateInput(
            candidate_id="1",
            source_type=CandidateSourceType.combined,
            source_ids=[],
            symbol="BTCUSDT",
            market_scope="spot",
            interval="1m",
            open_time=datetime.utcnow(),
            direction="LONG",
            signal_score=150.0,
            ml_blend_score=0.8,
            source_trace={"a": "b"},
            explanation="Test"
        )
    ]

    normalized = normalize_candidate_scores(candidates, config)
    assert len(normalized) == 1
    assert normalized[0].signal_score == 100.0 # Clamped
    assert normalized[0].ml_blend_score == 80.0 # Multiplied by 100
    assert normalized[0].direction == "long" # Lowercased
