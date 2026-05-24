from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskExecutionForbiddenError, RiskOrderObjectDetectedError
from binance50.risk.models import RiskIntent


def assert_no_order_object_created(payload: Any) -> None:
    if isinstance(payload, dict):
        if "order_id" in payload or "order_type" in payload:
            raise RiskOrderObjectDetectedError("Order object detected in payload")
        for _k, v in payload.items():
            assert_no_order_object_created(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_order_object_created(item)
    elif hasattr(payload, "model_dump"):
        assert_no_order_object_created(payload.model_dump())


def assert_no_position_sizing_output(payload: Any) -> None:
    if isinstance(payload, dict):
        if (
            "quantity" in payload
            or "qty" in payload
            or "base_qty" in payload
            or "quote_qty" in payload
        ):
            raise RiskExecutionForbiddenError("Position sizing output detected in payload")
        for _k, v in payload.items():
            assert_no_position_sizing_output(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_position_sizing_output(item)
    elif hasattr(payload, "model_dump"):
        assert_no_position_sizing_output(payload.model_dump())


def assert_no_stop_take_profit_output(payload: Any) -> None:
    if isinstance(payload, dict):
        if "stop_loss" in payload or "take_profit" in payload or "exit_price" in payload:
            raise RiskExecutionForbiddenError("Stop-loss or take-profit output detected in payload")
        for _k, v in payload.items():
            assert_no_stop_take_profit_output(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_stop_take_profit_output(item)
    elif hasattr(payload, "model_dump"):
        assert_no_stop_take_profit_output(payload.model_dump())


def assert_no_live_or_paper_intent(payload: Any) -> None:
    if isinstance(payload, dict):
        intent = payload.get("intent")
        if intent in ["live_trade", "paper_trade"]:  # Catch execution intents directly
            raise RiskExecutionForbiddenError(f"Execution intent detected: {intent}")
        for _k, v in payload.items():
            assert_no_live_or_paper_intent(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_live_or_paper_intent(item)
    elif hasattr(payload, "model_dump"):
        assert_no_live_or_paper_intent(payload.model_dump())
    elif hasattr(payload, "intent"):
        intent = payload.intent
        # Ensure it's using the safe enum values and not string representations of real actions
        if str(intent) in ["live_trade", "paper_trade"] or intent not in [
            i.value for i in RiskIntent
        ]:
            raise RiskExecutionForbiddenError(f"Execution intent detected: {intent}")


def build_risk_execution_guard_report(config: AppConfig) -> dict:
    return {
        "status": "active",
        "guards": [
            "no_order_object_created",
            "no_position_sizing_output",
            "no_stop_take_profit_output",
            "no_live_or_paper_intent",
        ],
    }
