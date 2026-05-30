import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionIntentError

from .models import (
    ExecutionIntentDraft,
    ExecutionIntentKind,
    ExecutionIntentStatus,
    ExecutionMode,
    ExecutionSide,
    ExecutionSourceType,
)
from .modes import assert_mode_can_create_draft, validate_mode_enabled


class ExecutionIntentBuilder:
    @staticmethod
    def build_sandbox_intent_draft(source: dict[str, Any], config: AppConfig) -> ExecutionIntentDraft:
        mode = ExecutionMode.sandbox
        validate_mode_enabled(mode, config)
        assert_mode_can_create_draft(mode, config)

        intent_id = f"intent_{uuid.uuid4().hex}"

        # In sandbox, hypothetical_notional_usdt might be passed via source
        hypothetical_notional = source.get("hypothetical_notional_usdt")
        if hypothetical_notional is not None:
             hypothetical_notional = Decimal(str(hypothetical_notional))

        # Side resolution
        side_val = source.get("side", "flat").lower()
        if side_val == "buy":
            side = ExecutionSide.buy
        elif side_val == "sell":
            side = ExecutionSide.sell
        else:
            side = ExecutionSide.flat

        return ExecutionIntentDraft(
            intent_id=intent_id,
            mode=mode,
            kind=ExecutionIntentKind.hypothetical_review,
            status=ExecutionIntentStatus.draft_created,
            source_type=ExecutionSourceType.portfolio_construction_sandbox,
            source_run_id=source.get("source_run_id", "unknown"),
            source_candidate_id=source.get("source_candidate_id", "unknown"),
            symbol=source.get("symbol", "UNKNOWN"),
            market_scope=source.get("market_scope", "spot"),
            interval=source.get("interval", "1m"),
            side=side,
            hypothetical_notional_usdt=hypothetical_notional,
            quantity=None,  # explicitly None
            price=None,     # explicitly None
            order_type=None,
            time_in_force=None,
            correlation_id=source.get("correlation_id", f"corr_{uuid.uuid4().hex}"),
            idempotency_key=source.get("idempotency_key", f"idk_{uuid.uuid4().hex}"),
            source_trace=source.get("source_trace", "Unknown Source Trace"),
            safety_scan_id=None,
            explanation=source.get("explanation", "Hypothetical sandbox execution intent."),
            metadata=source.get("metadata", {}),
            created_at_utc=datetime.now(timezone.utc),
        )

    @staticmethod
    def build_from_portfolio_construction_item(item: dict[str, Any], config: AppConfig) -> ExecutionIntentDraft:
        return ExecutionIntentBuilder.build_sandbox_intent_draft(item, config)

    @staticmethod
    def build_from_selected_candidate(candidate: Any, config: AppConfig) -> ExecutionIntentDraft:
        raise ExecutionIntentError("Direct candidate to execution draft is not implemented in this abstraction")

    @staticmethod
    def validate_intent_draft(intent: ExecutionIntentDraft, config: AppConfig) -> None:
        if config.execution.intents.reject_quantity_output_by_default and intent.quantity is not None:
            raise ExecutionIntentError("Quantity output is rejected by default.")
        if config.execution.intents.reject_price_output_by_default and intent.price is not None:
            raise ExecutionIntentError("Price output is rejected by default.")
        if config.execution.intents.reject_missing_symbol and not intent.symbol:
            raise ExecutionIntentError("Symbol is required.")
        if config.execution.intents.reject_missing_side and not intent.side:
            raise ExecutionIntentError("Side is required.")

        validate_mode_enabled(intent.mode, config)
        assert_mode_can_create_draft(intent.mode, config)

    @staticmethod
    def redact_intent(intent: ExecutionIntentDraft) -> dict[str, Any]:
        data = intent.__dict__.copy()
        # Ensure it doesn't accidentally serialize non-redactable things, but in P28 it's internal only
        data["created_at_utc"] = data["created_at_utc"].isoformat()
        if data.get("hypothetical_notional_usdt"):
            data["hypothetical_notional_usdt"] = float(data["hypothetical_notional_usdt"])
        return data
