import pytest
from binance50.config.models import AppConfig
from binance50.signals.models import ScoredSignalCandidate, ScoredSignalStatus, SignalDecisionIntent, SignalScoreTier
from binance50.signals.calibration import (
    build_calibration_placeholder_report, compute_brier_score_if_labels_available,
    compute_reliability_bins_if_labels_available, compute_expected_calibration_error_if_labels_available
)

@pytest.fixture
def config():
    return AppConfig()

def create_mock_scored(score):
    return ScoredSignalCandidate(
        scored_signal_id="s1", source_candidate_id="c1", symbol="BTCUSDT", market_scope="spot",
        interval="1m", open_time=0, direction="bullish", status=ScoredSignalStatus.scored_candidate,
        intent=SignalDecisionIntent.research_candidate, score=score, score_tier=SignalScoreTier.medium,
        confidence=80.0, plugin_name="plugin_a", plugin_type="trend_following", strategy_strength="medium"
    )

def test_placeholder_report(config):
    rep = build_calibration_placeholder_report(config)
    assert rep.calibration_training_deferred is True
    assert rep.sample_count == 0
    assert rep.metrics is None
    assert len(rep.warnings) > 0

def test_metrics_none_without_labels():
    scored = [create_mock_scored(50.0)]
    assert compute_brier_score_if_labels_available(scored) is None
    assert compute_reliability_bins_if_labels_available(scored) is None
    assert compute_expected_calibration_error_if_labels_available(scored) is None

def test_brier_score():
    scored = [create_mock_scored(90.0), create_mock_scored(10.0)]
    labels = [1, 0]
    # preds: [0.9, 0.1]
    # errs: [0.1, 0.1]
    # sq_errs: [0.01, 0.01] -> mean = 0.01
    score = compute_brier_score_if_labels_available(scored, labels)
    assert score is not None
    assert abs(score - 0.01) < 0.001

def test_reliability_bins():
    scored = [create_mock_scored(90.0), create_mock_scored(10.0)]
    labels = [1, 0]
    bins = compute_reliability_bins_if_labels_available(scored, labels, bins=2)
    assert bins is not None
    assert bins["bins"] == 2
    assert bins["counts"][0] == 1 # 0-0.5 bin
    assert bins["counts"][1] == 1 # 0.5-1.0 bin

def test_expected_calibration_error():
    scored = [create_mock_scored(90.0), create_mock_scored(10.0)]
    labels = [1, 0]
    ece = compute_expected_calibration_error_if_labels_available(scored, labels, bins=2)
    assert ece is not None
    assert abs(ece - 0.1) < 0.001
