import pytest

from binance50.core.exceptions import RiskExecutionForbiddenError, RiskOrderObjectDetectedError
from binance50.risk.models import RiskIntent
from binance50.safety.risk_execution_guard import (
    assert_no_live_or_paper_intent,
    assert_no_order_object_created,
    assert_no_position_sizing_output,
    assert_no_stop_take_profit_output,
)


def test_assert_no_order_object_created():
    safe_payload = {"risk_score": 50.0}
    assert_no_order_object_created(safe_payload)

    unsafe_payload = {"order_id": "12345", "risk_score": 50.0}
    with pytest.raises(RiskOrderObjectDetectedError):
        assert_no_order_object_created(unsafe_payload)


def test_assert_no_position_sizing_output():
    unsafe_payload = {"quantity": 1.5}
    with pytest.raises(RiskExecutionForbiddenError):
        assert_no_position_sizing_output(unsafe_payload)


def test_assert_no_stop_take_profit_output():
    unsafe_payload = {"stop_loss": 50000.0}
    with pytest.raises(RiskExecutionForbiddenError):
        assert_no_stop_take_profit_output(unsafe_payload)


def test_assert_no_live_or_paper_intent():
    safe_payload = {"intent": RiskIntent.risk_review}
    assert_no_live_or_paper_intent(safe_payload)

    unsafe_payload = {"intent": "live_trade"}
    with pytest.raises(RiskExecutionForbiddenError):
        assert_no_live_or_paper_intent(unsafe_payload)
