from binance50.config.models import AppConfig
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyExplanation,
    StrategyIntent,
    StrategyPluginType,
)
from binance50.strategies.quality import build_strategy_quality_report


def test_quality_duplicate_candidates():
    config = AppConfig()
    exp = StrategyExplanation(summary="test")
    c1 = SignalCandidate(
        candidate_id="duplicate_id",
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
    c2 = SignalCandidate(
        candidate_id="duplicate_id",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=100,
        plugin_name="test2",
        plugin_type=StrategyPluginType.trend_following,
        direction=StrategyDirection.bullish,
        strength=StrategyCandidateStrength.weak,
        confidence=50.0,
        explanation=exp,
        intent=StrategyIntent.no_order,
    )

    report = build_strategy_quality_report([c1, c2], config)
    assert report.duplicate_candidates == 1
    assert report.status == "fail"  # because reject_duplicate_candidates is True by default


def test_quality_empty_set():
    config = AppConfig()
    report = build_strategy_quality_report([], config)
    assert report.status == "pass"  # Because reject_empty is False by default
    assert len(report.issues) == 1
    assert report.issues[0].severity == "warning"
