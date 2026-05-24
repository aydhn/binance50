from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskConfigError, RiskExecutionForbiddenError
from binance50.risk.models import RiskAssessment, RiskRunResult
from binance50.risk.validators import validate_no_execution_fields


def assert_risk_config_safe(config: AppConfig) -> None:
    if not config.risk.enabled:
        return

    if not config.risk.execution_forbidden:
        raise RiskConfigError("Risk config error: execution_forbidden must be True")
    if not config.risk.order_creation_forbidden:
        raise RiskConfigError("Risk config error: order_creation_forbidden must be True")
    if not config.risk.live_trade_forbidden:
        raise RiskConfigError("Risk config error: live_trade_forbidden must be True")
    if not config.risk.paper_trade_forbidden:
        raise RiskConfigError("Risk config error: paper_trade_forbidden must be True")
    if not config.risk.backtest_forbidden:
        raise RiskConfigError("Risk config error: backtest_forbidden must be True")

    if config.risk.account.allow_real_balance_fetch:
        raise RiskConfigError("Risk config error: allow_real_balance_fetch must be False")
    if config.risk.account.allow_account_api:
        raise RiskConfigError("Risk config error: allow_account_api must be False")

    pos = config.risk.position_risk
    if (
        pos.produce_order_quantity
        or pos.produce_entry_price
        or pos.produce_exit_price
        or pos.produce_stop_loss
        or pos.produce_take_profit
    ):
        raise RiskConfigError(
            "Risk config error: production of order/execution fields must be False"
        )


def assert_risk_input_safe(
    scored_signals: list[Any], regimes: list[Any] | None, config: AppConfig
) -> None:
    assert_risk_config_safe(config)
    for sig in scored_signals:
        validate_no_execution_fields(sig)
    if regimes:
        for r in regimes:
            validate_no_execution_fields(r)


def assert_risk_assessment_safe(assessment: RiskAssessment, config: AppConfig) -> None:
    validate_no_execution_fields(assessment)
    if "order" in assessment.explanation.lower() and config.risk.quality.reject_order_like_language:
        # A simple check; quality check handles this more comprehensively
        raise RiskExecutionForbiddenError("Order-like language detected in risk explanation")


def assert_risk_output_safe(result: RiskRunResult, config: AppConfig) -> None:
    validate_no_execution_fields(result)
    for a in result.assessments:
        assert_risk_assessment_safe(a, config)
    for a in result.rejected_assessments:
        assert_risk_assessment_safe(a, config)


def build_risk_safety_report(config: AppConfig) -> dict:
    return {
        "execution_forbidden": config.risk.execution_forbidden,
        "real_balance_disabled": not config.risk.account.allow_real_balance_fetch,
        "order_creation_disabled": config.risk.order_creation_forbidden,
    }
