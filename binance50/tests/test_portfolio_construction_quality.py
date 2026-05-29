import pytest
from binance50.config.models import AppConfig, PortfolioConstructionConfig
from binance50.portfolio.construction.models import PortfolioConstructionRunResult, PortfolioAllocationItem, PortfolioAllocationMethod, PortfolioConstructionRunRequest
from binance50.portfolio.construction.quality import build_portfolio_construction_quality_report, assert_portfolio_construction_quality_passed
from binance50.core.exceptions import PortfolioConstructionQualityError

@pytest.fixture
def base_config():
    config = AppConfig()
    config.portfolio_construction = PortfolioConstructionConfig()
    return config

def create_mock_result(item_overrides=None):
    req = PortfolioConstructionRunRequest(symbol="BTC", market_scope="spot", interval="1m", portfolio_selection_run_id="test", request_id="r", correlation_id="c")
    item = PortfolioAllocationItem(
        allocation_item_id="1", candidate_id="c1", selected_candidate_id="sc1", symbol="BTC",
        market_scope="spot", interval="1m", direction="long", method=PortfolioAllocationMethod.equal_weight,
        sandbox_weight=0.5, hypothetical_notional_usdt=100.0, hypothetical_capital_pct=50.0,
        volatility_estimate_pct=0.0, marginal_risk_contribution=0.0, component_risk_contribution=0.0,
        percent_risk_contribution=0.0, explanation="Hypothetical allocation"
    )
    if item_overrides:
        for k, v in item_overrides.items():
            setattr(item, k, v)
    return PortfolioConstructionRunResult(request=req, run_id="r1", status="completed", selected_sandbox_allocation=[item])

def test_quality_passed(base_config):
    result = create_mock_result()
    report = build_portfolio_construction_quality_report(result, base_config)
    assert report.status == "passed"
    assert_portfolio_construction_quality_passed(report, base_config)

def test_quality_failed_missing_explanation(base_config):
    result = create_mock_result({"explanation": ""})
    report = build_portfolio_construction_quality_report(result, base_config)
    assert report.status == "failed"
    assert report.missing_explanation_count == 1
    with pytest.raises(PortfolioConstructionQualityError):
        assert_portfolio_construction_quality_passed(report, base_config)

def test_quality_failed_order_like_output(base_config):
    result = create_mock_result({"explanation": "Will execute a buy order now."})
    report = build_portfolio_construction_quality_report(result, base_config)
    assert report.status == "failed"
    assert report.order_like_output_count > 0
    with pytest.raises(PortfolioConstructionQualityError):
        assert_portfolio_construction_quality_passed(report, base_config)
