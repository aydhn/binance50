import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.blending.models import MLBlendBreakdown
from binance50.ml.blending.sandbox_candidates import build_blended_sandbox_candidate, validate_blended_sandbox_candidate, candidates_to_dataframe, dataframe_to_candidates

def test_sandbox_candidate_build():
    config = AppConfig()
    row = pd.Series({"symbol": "BTCUSDT", "market_scope": "spot", "interval": "1m", "open_time": 0, "close_time": 0})
    breakdown = MLBlendBreakdown(final_blended_score=50.0, final_blended_probability=0.5)
    cand = build_blended_sandbox_candidate(row, 50.0, 0.5, breakdown, "test", config)
    assert cand.symbol == "BTCUSDT"
    assert cand.blocked_from_signal_engine is True

def test_validate_blended_sandbox_candidate():
    config = AppConfig()
    row = pd.Series({"symbol": "BTCUSDT", "market_scope": "spot", "interval": "1m", "open_time": 0, "close_time": 0})
    breakdown = MLBlendBreakdown(final_blended_score=50.0, final_blended_probability=0.5)
    cand = build_blended_sandbox_candidate(row, 50.0, 0.5, breakdown, "test", config)
    validate_blended_sandbox_candidate(cand, config) # Should not raise
    cand.blocked_from_signal_engine = False
    with pytest.raises(ValueError):
        validate_blended_sandbox_candidate(cand, config)

def test_dataframe_roundtrip():
    config = AppConfig()
    row = pd.Series({"symbol": "BTCUSDT", "market_scope": "spot", "interval": "1m", "open_time": 0, "close_time": 0})
    breakdown = MLBlendBreakdown(final_blended_score=50.0, final_blended_probability=0.5)
    cand = build_blended_sandbox_candidate(row, 50.0, 0.5, breakdown, "test", config)
    df = candidates_to_dataframe([cand])
    cands = dataframe_to_candidates(df)
    assert len(cands) == 1
    assert cands[0].symbol == "BTCUSDT"
