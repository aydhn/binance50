import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.signals.conflicts import detect_opposite_direction_conflicts, detect_same_plugin_conflicts, compute_conflict_penalty, mark_conflicted_scored_candidates
from binance50.signals.models import ScoredSignalCandidate, SignalScoreTier, SignalDecisionIntent, ScoredSignalStatus
from binance50.strategies.models import SignalCandidate, StrategyDirection, StrategyCandidateStrength, StrategyPluginType, StrategyExplanation

@pytest.fixture
def config():
    c = AppConfig()
    c.signals.conflicts.bearish_bullish_conflict_penalty = 20.0
    c.signals.conflicts.same_plugin_conflict_penalty = 30.0
    c.signals.conflicts.max_conflict_penalty = 50.0
    c.signals.component_weights["conflict_penalty"] = -0.2
    return c

@pytest.fixture
def candidates():
    dt = datetime.now()
    exp = StrategyExplanation(summary="test")
    return [
        SignalCandidate(
            candidate_id="c1", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_a", plugin_type=StrategyPluginType.trend_following,
            direction=StrategyDirection.bullish, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        ),
        SignalCandidate(
            candidate_id="c2", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_b", plugin_type=StrategyPluginType.mean_reversion,
            direction=StrategyDirection.bearish, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        ),
        SignalCandidate(
            candidate_id="c3", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_a", plugin_type=StrategyPluginType.trend_following,
            direction=StrategyDirection.bearish, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        ),
        SignalCandidate(
            candidate_id="c4", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_c", plugin_type=StrategyPluginType.volume_confirmation,
            direction=StrategyDirection.neutral, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        )
    ]

def test_detect_opposite_direction_conflicts(config, candidates):
    conflicts = detect_opposite_direction_conflicts(candidates, config)
    assert len(conflicts) == 1
    assert conflicts[0].penalty == 20.0
    assert "c1" in conflicts[0].bullish_candidate_ids
    assert "c2" in conflicts[0].bearish_candidate_ids or "c3" in conflicts[0].bearish_candidate_ids

def test_detect_same_plugin_conflicts(config, candidates):
    conflicts = detect_same_plugin_conflicts(candidates, config)
    assert len(conflicts) == 1
    assert conflicts[0].penalty == 30.0
    assert conflicts[0].same_plugin_conflicts is True
    assert "c1" in conflicts[0].bullish_candidate_ids
    assert "c3" in conflicts[0].bearish_candidate_ids

def test_compute_conflict_penalty(config, candidates):
    conflicts = detect_opposite_direction_conflicts(candidates, config) + detect_same_plugin_conflicts(candidates, config)

    # c1 is involved in both conflicts (20.0 + 30.0 = 50.0) -> cap at 50.0
    # penalty raw = 50.0, weight = -0.2 -> contribution = -10.0
    penalty = compute_conflict_penalty(candidates[0], conflicts, config)
    assert penalty.raw_value == 50.0
    assert penalty.contribution == -10.0

def test_neutral_no_conflict(config, candidates):
    conflicts = detect_opposite_direction_conflicts(candidates, config)
    penalty = compute_conflict_penalty(candidates[3], conflicts, config) # c4 is neutral
    assert penalty.raw_value == 0.0
    assert penalty.contribution == 0.0

def test_mark_conflicted_scored_candidates(config, candidates):
    conflicts = detect_same_plugin_conflicts(candidates, config)
    scored = [
        ScoredSignalCandidate(
            scored_signal_id="s1", source_candidate_id="c1", symbol="BTCUSDT", market_scope="spot",
            interval="1m", open_time=datetime.now(), direction="bullish", status=ScoredSignalStatus.scored_candidate,
            intent=SignalDecisionIntent.research_candidate, score=50.0, score_tier=SignalScoreTier.medium,
            confidence=80.0, plugin_name="plugin_a", plugin_type="trend_following", strategy_strength="medium"
        )
    ]
    marked = mark_conflicted_scored_candidates(scored, conflicts)
    assert marked[0].conflicted is True
    assert len(marked[0].conflict_reasons) > 0
