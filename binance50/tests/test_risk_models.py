from datetime import datetime

import pytest
from pydantic import ValidationError

from binance50.risk.models import (
    RiskAssessment,
    RiskAssessmentStatus,
    RiskBreakdown,
    RiskComponent,
    RiskDimension,
    RiskIntent,
    RiskSeverity,
)


def test_risk_component_valid():
    comp = RiskComponent(
        dimension=RiskDimension.signal_score,
        raw_value=85.0,
        passed=True,
        severity=RiskSeverity.info,
        reason="Good score",
        metadata={"threshold": 60.0},
    )
    assert comp.dimension == RiskDimension.signal_score
    assert comp.passed is True


def test_risk_assessment_no_execution_fields():
    breakdown = RiskBreakdown(final_risk_score=70.0)

    # Valid assessment
    ass = RiskAssessment(
        assessment_id="test1",
        source_scored_signal_id="sig1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        close_time=datetime.utcnow(),
        direction="bullish",
        status=RiskAssessmentStatus.needs_review,
        intent=RiskIntent.risk_review,
        final_risk_score=70.0,
        risk_tier="medium",
        approved=False,
        blocked=False,
        needs_review=True,
        breakdown=breakdown,
        explanation="Review needed",
    )
    assert ass.status == RiskAssessmentStatus.needs_review

    # Invalid: try adding execution field in metadata
    with pytest.raises(ValidationError):
        ass = RiskAssessment(
            assessment_id="test2",
            source_scored_signal_id="sig2",
            symbol="BTCUSDT",
            market_scope="spot",
            interval="1m",
            open_time=datetime.utcnow(),
            close_time=datetime.utcnow(),
            direction="bullish",
            status=RiskAssessmentStatus.needs_review,
            intent=RiskIntent.risk_review,
            final_risk_score=70.0,
            risk_tier="medium",
            approved=False,
            blocked=False,
            needs_review=True,
            breakdown=breakdown,
            explanation="Review needed",
            metadata={"quantity": 1.0},  # Forbidden
        )
