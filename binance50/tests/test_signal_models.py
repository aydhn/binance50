import pytest
from binance50.signals.models import (
    ScoredSignalCandidate, SignalScoreComponent, SignalScoreBreakdown,
    ConfluenceGroup, ScoredSignalStatus, SignalScoreTier, SignalDecisionIntent
)
from binance50.strategies.models import SignalCandidate, StrategyDirection, StrategyCandidateStrength, StrategyPluginType, StrategyIntent
from datetime import datetime

def test_signal_score_component_valid():
    comp = SignalScoreComponent(
        name="test_comp",
        raw_value=50.0,
        normalized_value=50.0,
        weight=1.0,
        contribution=50.0,
        reason="testing"
    )
    assert comp.name == "test_comp"
    assert comp.contribution == 50.0

def test_signal_score_breakdown_valid():
    comp = SignalScoreComponent(
        name="test_comp",
        raw_value=50.0,
        normalized_value=50.0,
        weight=1.0,
        contribution=50.0,
        reason="testing"
    )
    breakdown = SignalScoreBreakdown(
        components=[comp],
        subtotal_before_penalties=50.0,
        total_penalty=0.0,
        final_score=50.0,
        score_tier=SignalScoreTier.medium
    )
    assert breakdown.final_score == 50.0
    assert breakdown.score_tier == SignalScoreTier.medium

def test_scored_signal_candidate_valid():
    dt = datetime.now()
    scored = ScoredSignalCandidate(
        scored_signal_id="score_1",
        source_candidate_id="cand_1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=dt,
        direction="bullish",
        status=ScoredSignalStatus.scored_candidate,
        intent=SignalDecisionIntent.research_candidate,
        score=55.0,
        score_tier=SignalScoreTier.medium,
        confidence=60.0,
        plugin_name="test_plugin",
        plugin_type="trend_following",
        strategy_strength="medium"
    )
    assert scored.score == 55.0
    assert scored.intent == SignalDecisionIntent.research_candidate

def test_scored_signal_candidate_score_validation():
    with pytest.raises(ValueError):
        ScoredSignalCandidate(
            scored_signal_id="score_1",
            source_candidate_id="cand_1",
            symbol="BTCUSDT",
            market_scope="spot",
            interval="1m",
            open_time=datetime.now(),
            direction="bullish",
            status=ScoredSignalStatus.scored_candidate,
            intent=SignalDecisionIntent.research_candidate,
            score=150.0, # out of bounds
            score_tier=SignalScoreTier.very_high,
            confidence=60.0,
            plugin_name="test_plugin",
            plugin_type="trend_following",
            strategy_strength="medium"
        )
