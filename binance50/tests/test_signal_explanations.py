from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.signals.explanations import (
    build_confluence_explanation,
    build_score_breakdown_explanation,
    build_score_explanation,
    validate_scored_signal_explanation,
)
from binance50.signals.models import (
    ScoredSignalCandidate,
    ScoredSignalStatus,
    SignalDecisionIntent,
    SignalScoreBreakdown,
    SignalScoreComponent,
    SignalScoreTier,
)


@pytest.fixture
def scored():
    breakdown = SignalScoreBreakdown(
        components=[
            SignalScoreComponent(
                name="c1",
                raw_value=50.0,
                normalized_value=50.0,
                weight=1.0,
                contribution=50.0,
                reason="r1",
            )
        ],
        subtotal_before_penalties=50.0,
        total_penalty=0.0,
        final_score=50.0,
        score_tier=SignalScoreTier.medium,
    )

    return ScoredSignalCandidate(
        scored_signal_id="s1",
        source_candidate_id="c1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.now(),
        direction="bullish",
        status=ScoredSignalStatus.scored_candidate,
        intent=SignalDecisionIntent.research_candidate,
        score=50.0,
        score_tier=SignalScoreTier.medium,
        confidence=80.0,
        plugin_name="plugin_a",
        plugin_type="trend_following",
        strategy_strength="medium",
        score_breakdown=breakdown,
        explanation="Candidate generated safely",
    )


def test_build_score_breakdown_explanation(scored):
    exp = build_score_breakdown_explanation(scored.score_breakdown)
    assert exp["final_score"] == 50.0
    assert exp["components"][0]["name"] == "c1"


def test_build_confluence_explanation():
    assert build_confluence_explanation(None) == "No confluence detected."


def test_build_score_explanation(scored):
    exp = build_score_explanation(scored)
    assert "Candidate c1 from plugin plugin_a" in exp
    assert "Breakdown:" in exp
    assert "- c1: 50.00 (r1)" in exp


def test_validate_scored_signal_explanation(scored):
    config = AppConfig()
    # This should pass without raising
    validate_scored_signal_explanation(scored, config)

    # Try forbidden word
    from binance50.core.exceptions import ActionableLanguageDetectedError

    bad_scored = scored.model_copy(update={"explanation": "You should buy now based on this."})
    with pytest.raises(ActionableLanguageDetectedError):
        validate_scored_signal_explanation(bad_scored, config)
