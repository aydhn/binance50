import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionBoundaryError
from binance50.execution.boundaries import (
    assert_portfolio_allocation_not_order_payload,
    assert_sandbox_candidate_not_order,
    assert_ml_blend_not_order,
    assert_risk_assessment_not_order,
    assert_no_direct_flow_to_gateway,
    build_execution_boundary_report
)

def test_boundary_portfolio_allocation():
    config = get_config()
    with pytest.raises(ExecutionBoundaryError):
        assert_portfolio_allocation_not_order_payload({"quantity": 10}, config)

def test_boundary_sandbox_candidate():
    config = get_config()
    with pytest.raises(ExecutionBoundaryError):
        assert_sandbox_candidate_not_order({"order_type": "MARKET"}, config)

def test_boundary_report_passed():
    config = get_config()
    report = build_execution_boundary_report({"symbol": "BTCUSDT"}, config)
    assert report["passed"] is True
