from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import IntentPromotionForbiddenError

from binance50.execution.promotion import IntentPromotionReport


def assert_promotion_disabled(config: AppConfig) -> None:
    if not config.execution.kill_switch.block_intent_promotion:
        raise IntentPromotionForbiddenError("Intent promotion block must be enabled in Phase 28.")


def assert_no_paper_testnet_live_promotion(report: IntentPromotionReport) -> None:
    if report.allowed:
        raise IntentPromotionForbiddenError("Intent promotion to paper/testnet/live is forbidden.")


def assert_promotion_requires_future_phase_guards(report: IntentPromotionReport) -> None:
    if not report.required_future_guards:
        raise IntentPromotionForbiddenError("Promotion request did not specify required future phase guards.")


def build_intent_promotion_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "promotion_blocked": config.execution.kill_switch.block_intent_promotion
    }
