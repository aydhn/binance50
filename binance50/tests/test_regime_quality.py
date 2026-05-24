import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeQualityError
from binance50.regimes.models import (
    MarketRegime,
    RegimeClassification,
    RegimeFamily,
    RegimeMethod,
    RegimeRiskContext,
)
from binance50.regimes.quality import (
    RegimeQualityIssue,
    RegimeQualityReport,
    assert_regime_quality_passed,
    detect_missing_explanations,
)


def test_missing_explanation():
    c = RegimeClassification(
        regime_id="1",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=1,
        close_time=2,
        regime=MarketRegime.trend_up,
        family=RegimeFamily.trend,
        method=RegimeMethod.rule_based,
        confidence=50,
        risk_context=RegimeRiskContext.unknown,
        explanation={},
        feature_snapshot={},
        created_at_utc=0,
    )
    issues = detect_missing_explanations([c])
    assert len(issues) == 1


def test_quality_assert():
    config = AppConfig()
    r = RegimeQualityReport(
        status="failed",
        row_count=1,
        classification_count=1,
        unknown_count=0,
        transition_count=0,
        transition_ratio=0.0,
        missing_explanation_count=1,
        confidence_out_of_range_count=0,
        lookahead_risk_count=0,
        issues=[RegimeQualityIssue(issue_type="err", severity="error", open_time=0, message="err")],
        generated_at_utc=0,
    )
    with pytest.raises(RegimeQualityError):
        assert_regime_quality_passed(r, config)
