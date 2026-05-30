import uuid
from decimal import Decimal
from typing import Optional

from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderSide, PaperOrderType, PaperTimeInForce
from binance50.execution.models import ExecutionIntentDraft
from binance50.core.exceptions import PaperIntentError

class PaperIntentBridge:
    def build_paper_order_from_execution_intent(self, intent: ExecutionIntentDraft, config: AppConfig) -> PaperOrder:
        self.validate_execution_intent_for_paper(intent, config)

        # Hardcode some dummy values for simulation bridge
        paper_order_id = f"{config.paper_execution.order.internal_order_id_prefix}{uuid.uuid4().hex[:8]}"

        return PaperOrder(
            paper_order_id=paper_order_id,
            source_intent_id=intent.intent_id,
            source_run_id=intent.run_id,
            symbol=intent.symbol,
            market_scope=intent.market_scope,
            interval=intent.interval,
            side=PaperOrderSide(intent.side.value),
            order_type=PaperOrderType(config.paper_execution.order.default_order_type),
            time_in_force=PaperTimeInForce(config.paper_execution.order.default_time_in_force),
            requested_notional_usdt=intent.requested_notional_usdt,
            requested_quantity=self.convert_hypothetical_notional_to_requested_quantity(intent, Decimal("1000.0"), {}, config),
            created_open_time=intent.open_time,
            correlation_id=intent.correlation_id,
            idempotency_key=intent.idempotency_key,
            source_trace=intent.source_trace,
            explanation=self.build_paper_order_explanation(intent)
        )

    def validate_execution_intent_for_paper(self, intent: ExecutionIntentDraft, config: AppConfig) -> None:
        if config.paper_execution.intent.reject_live_testnet_intent and intent.intent_mode.value in ["live_candidate", "testnet_candidate"]:
            raise PaperIntentError(f"Live/testnet intent rejected: {intent.intent_mode}")

        if config.paper_execution.intent.require_source_trace and not intent.source_trace:
            raise PaperIntentError("Source trace is required for paper intent conversion")

    def convert_hypothetical_notional_to_requested_quantity(self, intent: ExecutionIntentDraft, market_price: Decimal, symbol_filters: dict, config: AppConfig) -> Decimal:
        return intent.requested_notional_usdt / market_price

    def build_paper_order_explanation(self, intent: ExecutionIntentDraft) -> str:
        return f"Converted from intent {intent.intent_id}"

    def validate_paper_order(self, order: PaperOrder, config: AppConfig) -> None:
        if config.paper_execution.order.exchange_order_id_forbidden and "exchange_order_id" in order.metadata:
            raise PaperIntentError("Exchange order ID is forbidden in paper order")
