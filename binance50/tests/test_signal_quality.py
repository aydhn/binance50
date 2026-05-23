import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.signals.quality import (
    build_signal_quality_report, assert_signal_quality_passed,
    detect_score_out_of_range, detect_missing_breakdowns, detect_execution_intent
)
from binance50.signals.models import ScoredSignalCandidate, SignalScoreTier, SignalDecisionIntent, ScoredSignalStatus, SignalScoringResult, SignalScoringRequest, SignalScoringMetadata

@pytest.fixture
def config():
    return AppConfig()

def create_mock(score, intent="research_candidate", breakdown=True, exp="Test"):
    from binance50.signals.models import SignalScoreBreakdown
    bd = SignalScoreBreakdown(components=[], subtotal_before_penalties=score, total_penalty=0.0, final_score=score, score_tier=SignalScoreTier.medium) if breakdown else None

    return ScoredSignalCandidate.model_construct(
        scored_signal_id="s1", source_candidate_id="c1", symbol="BTCUSDT", market_scope="spot",
        interval="1m", open_time=datetime.now(), direction="bullish", status=ScoredSignalStatus.scored_candidate,
        intent=SignalDecisionIntent(intent), score=score, score_tier=SignalScoreTier.medium,
        confidence=80.0, plugin_name="plugin_a", plugin_type="trend_following", strategy_strength="medium",
        score_breakdown=bd, explanation=exp
    )

def test_detect_score_out_of_range(config):
    scored = [create_mock(150.0), create_mock(50.0)]
    issues = detect_score_out_of_range(scored, config)
    assert len(issues) == 1
    assert issues[0].issue_type == "score_out_of_range"

def test_detect_missing_breakdowns(config):
    scored = [create_mock(50.0, breakdown=False)]
    issues = detect_missing_breakdowns(scored, config)
    assert len(issues) == 1

def test_build_signal_quality_report(config):
    scored = [create_mock(50.0)]
    report = build_signal_quality_report(scored, config)
    assert report.status == "passed"
    assert len(report.issues) == 0

def test_assert_signal_quality_passed(config):
    scored = [create_mock(150.0)] # will cause out of range error
    report = build_signal_quality_report(scored, config)

    from binance50.core.exceptions import SignalQualityError
    with pytest.raises(SignalQualityError):
        assert_signal_quality_passed(report, config)
