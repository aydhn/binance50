from binance50.strategies.explanations import (
    build_explanation_summary,
    build_human_readable_explanation,
)
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyConditionEvidence,
    StrategyDirection,
    StrategyExplanation,
    StrategyIntent,
    StrategyPluginType,
)


def test_build_explanation_summary():
    evidence = [
        StrategyConditionEvidence(feature_name="rsi", operator="gt", passed=True),
        StrategyConditionEvidence(feature_name="macd", operator="gt", passed=False),
    ]
    summary = build_explanation_summary("test_plugin", StrategyDirection.bullish, evidence)
    assert "test_plugin" in summary
    assert "bullish" in summary
    assert "rsi" in summary
    assert "macd" in summary


def test_human_readable_explanation():
    exp = StrategyExplanation(summary="test")
    c = SignalCandidate(
        candidate_id="1",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=100,
        plugin_name="test",
        plugin_type=StrategyPluginType.trend_following,
        direction=StrategyDirection.bullish,
        strength=StrategyCandidateStrength.weak,
        confidence=50.0,
        explanation=exp,
        intent=StrategyIntent.no_order,
    )
    hr = build_human_readable_explanation(c)
    assert "Analysis for BTC" in hr
    assert "BULLISH" in hr
    assert "buy now" not in hr.lower()
