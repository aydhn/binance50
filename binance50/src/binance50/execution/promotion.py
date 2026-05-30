from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import IntentPromotionForbiddenError

from .models import ExecutionIntentDraft, ExecutionMode


@dataclass
class IntentPromotionRequest:
    source_intent_id: str
    from_mode: str
    to_mode: str
    reason: str
    requested_by: str
    created_at_utc: datetime
    metadata: dict[str, Any]


@dataclass
class IntentPromotionReport:
    request: IntentPromotionRequest
    allowed: bool
    blocked: bool
    reasons: list[str]
    required_future_guards: list[str]
    metadata: dict[str, Any]


def validate_promotion_request(request: IntentPromotionRequest, config: AppConfig) -> None:
    if not request.source_intent_id:
        raise IntentPromotionForbiddenError("Source intent ID is missing.")
    if not request.to_mode:
        raise IntentPromotionForbiddenError("Target mode is missing.")


def block_all_promotions_phase28(request: IntentPromotionRequest, config: AppConfig) -> IntentPromotionReport:
    return IntentPromotionReport(
        request=request,
        allowed=False,
        blocked=True,
        reasons=["All intent promotion is blocked in Phase 28."],
        required_future_guards=["paper_engine_integration", "live_risk_checks", "exchange_routing"],
        metadata={}
    )


def request_intent_promotion(intent: ExecutionIntentDraft, to_mode: ExecutionMode, reason: str, config: AppConfig) -> IntentPromotionReport:
    req = IntentPromotionRequest(
        source_intent_id=intent.intent_id,
        from_mode=intent.mode.value,
        to_mode=to_mode.value,
        reason=reason,
        requested_by="system",
        created_at_utc=datetime.now(timezone.utc),
        metadata={}
    )
    validate_promotion_request(req, config)

    report = block_all_promotions_phase28(req, config)
    if report.blocked:
        raise IntentPromotionForbiddenError(f"Promotion rejected: {report.reasons}")

    return report


def build_promotion_policy_report(config: AppConfig) -> dict[str, Any]:
    return {
        "sandbox_to_paper": "blocked_in_phase_28",
        "sandbox_to_testnet": "blocked_in_phase_28",
        "sandbox_to_live": "blocked_in_phase_28",
        "paper_to_testnet": "blocked_in_phase_28",
        "testnet_to_live": "blocked_in_phase_28",
    }
