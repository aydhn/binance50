from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionBoundaryError


def assert_portfolio_allocation_not_order_payload(payload: dict[str, Any], config: AppConfig) -> None:
    if config.execution.boundaries.portfolio_allocation_to_execution_direct_flow_forbidden:
        if "quantity" in payload or "price" in payload or "order_id" in payload:
            raise ExecutionBoundaryError("Portfolio allocation payload contains direct execution fields.")


def assert_sandbox_candidate_not_order(payload: dict[str, Any], config: AppConfig) -> None:
    if config.execution.boundaries.sandbox_candidate_to_order_forbidden:
        if "order_type" in payload or "time_in_force" in payload:
            raise ExecutionBoundaryError("Sandbox candidate payload cannot be treated as an order.")


def assert_ml_blend_not_order(payload: dict[str, Any], config: AppConfig) -> None:
    if config.execution.boundaries.ml_blend_to_order_forbidden:
        if "submit_order" in payload or "live_order" in payload:
            raise ExecutionBoundaryError("ML blend output cannot be treated as an order.")


def assert_risk_assessment_not_order(payload: dict[str, Any], config: AppConfig) -> None:
    if config.execution.boundaries.risk_assessment_to_order_forbidden:
        if "client_order_id" in payload or "leverage_to_set" in payload:
            raise ExecutionBoundaryError("Risk assessment payload cannot contain actionable execution commands.")


def assert_no_direct_flow_to_gateway(payload: dict[str, Any], config: AppConfig) -> None:
    if config.execution.boundaries.exchange_gateway_default_disabled:
        if "gateway_call" in payload or "api_request" in payload:
            raise ExecutionBoundaryError("Direct flow to gateway is forbidden in Phase 28.")


def build_execution_boundary_report(payload: dict[str, Any], config: AppConfig) -> dict[str, Any]:
    try:
        assert_portfolio_allocation_not_order_payload(payload, config)
        assert_sandbox_candidate_not_order(payload, config)
        assert_ml_blend_not_order(payload, config)
        assert_risk_assessment_not_order(payload, config)
        assert_no_direct_flow_to_gateway(payload, config)
        return {"passed": True, "violations": []}
    except ExecutionBoundaryError as e:
        return {"passed": False, "violations": [str(e)]}
