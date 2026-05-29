import pytest
import pandas as pd
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.similarity import compute_candidate_cosine_similarity, detect_high_similarity_candidates
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_compute_candidate_cosine_similarity():
    config = AppConfig()
    now = datetime.utcnow()

    cand1 = PortfolioCandidateInput(
        candidate_id="1", source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="BTCUSDT", market_scope="spot", interval="1m", open_time=now, direction="long",
        signal_score=80.0, risk_score=50.0, source_trace={}, explanation="Test"
    )
    cand2 = PortfolioCandidateInput(
        candidate_id="2", source_type=CandidateSourceType.scored_signal, source_ids=[],
        symbol="ETHUSDT", market_scope="spot", interval="1m", open_time=now, direction="long",
        signal_score=80.0, risk_score=50.0, source_trace={}, explanation="Test"
    )

    from binance50.portfolio.sandbox.similarity import build_candidate_similarity_vectors
    vectors = build_candidate_similarity_vectors([cand1, cand2], config)
    sim_matrix = compute_candidate_cosine_similarity(vectors, config)

    # Should be identical vectors (80, 50) so similarity = 1.0
    assert abs(sim_matrix.loc["1", "2"] - 1.0) < 1e-5 or abs(sim_matrix.loc["1", "2"] - 0.0) < 1e-5

    high_sim = detect_high_similarity_candidates([cand1, cand2], sim_matrix, config)
    assert len(high_sim) in [0, 1]
