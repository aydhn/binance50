import pytest

from binance50.config.models import AppConfig
from binance50.risk.explanations import (
    build_risk_breakdown_explanation,
    build_risk_explanation,
    explain_blocking_reasons,
    explain_risk_status,
    validate_risk_explanation,
)
from binance50.risk.models import RiskAssessmentStatus, RiskBreakdown


@pytest.fixture
def test_config():
    return AppConfig()


def test_explanations():
    assert "approved for paper" in explain_risk_status(
        RiskAssessmentStatus.approved_for_paper_review
    )

    breakdown = RiskBreakdown(
        blocking_reasons=["High leverage", "Spread too high"], warnings=["Volatile regime"]
    )
    assert "High leverage" in explain_blocking_reasons(breakdown)

    full_explanation = build_risk_explanation(RiskAssessmentStatus.blocked_by_policy, breakdown)
    assert "Blocked due to" in full_explanation
    assert "Warnings: 1" in full_explanation

    bd_exp = build_risk_breakdown_explanation(breakdown)
    assert bd_exp["blocks"] == ["High leverage", "Spread too high"]


def test_validate_risk_explanation(test_config):
    test_config.risk.quality.reject_order_like_language = True

    # Safe text
    validate_risk_explanation("This is a safe assessment for review", test_config)

    # Unsafe text
    with pytest.raises(ValueError):
        validate_risk_explanation("We should buy this now", test_config)
