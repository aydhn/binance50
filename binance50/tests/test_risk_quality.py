from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskQualityError
from binance50.risk.models import RiskAssessment, RiskAssessmentStatus, RiskBreakdown, RiskIntent
from binance50.risk.quality import assert_risk_quality_passed, build_risk_quality_report


@pytest.fixture
def test_config():
    return AppConfig()


def test_risk_quality_report(test_config):
    # Assessment missing explanation
    a1 = RiskAssessment(
        assessment_id="1",
        source_scored_signal_id="s1",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        close_time=datetime.utcnow(),
        direction="bullish",
        status=RiskAssessmentStatus.needs_review,
        intent=RiskIntent.risk_review,
        final_risk_score=60.0,
        risk_tier="low",
        approved=False,
        blocked=False,
        needs_review=True,
        breakdown=RiskBreakdown(),
        explanation="",
    )

    # Assessment with out-of-range score and order language
    a2 = RiskAssessment(
        assessment_id="2",
        source_scored_signal_id="s2",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        close_time=datetime.utcnow(),
        direction="bullish",
        status=RiskAssessmentStatus.needs_review,
        intent=RiskIntent.risk_review,
        final_risk_score=150.0,
        risk_tier="low",
        approved=False,
        blocked=False,
        needs_review=True,
        breakdown=RiskBreakdown(),
        explanation="We should short this",
    )

    report = build_risk_quality_report([a1, a2], test_config)

    assert report.missing_explanation_count == 1
    assert report.order_language_count == 1
    assert report.score_out_of_range_count == 1
    assert report.status == "failed"

    with pytest.raises(RiskQualityError):
        assert_risk_quality_passed(report, test_config)
