from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.paper.models import PaperExecutionMode, PaperOrder, PaperOrderStatus
from binance50.paper.lifecycle import transition_paper_order

class LocalPaperGateway:
    def name(self) -> str:
        return "local_paper_gateway"

    def mode(self) -> PaperExecutionMode:
        return PaperExecutionMode.local_paper

    def is_networked(self) -> bool:
        return False

    def submit_paper_order(self, order: PaperOrder, market_data: dict, config: AppConfig) -> PaperOrder:
        order = transition_paper_order(order, PaperOrderStatus.paper_submitted_local, config)
        order.submitted_at_utc = datetime.now(timezone.utc)
        order = transition_paper_order(order, PaperOrderStatus.paper_accepted_local, config)
        return order

    def cancel_paper_order(self, order: PaperOrder, config: AppConfig) -> PaperOrder:
        order = transition_paper_order(order, PaperOrderStatus.paper_canceled_local, config)
        order.updated_at_utc = datetime.now(timezone.utc)
        return order

    def health(self) -> dict:
        return {"status": "healthy", "networked": False}

    def safety_report(self) -> dict:
        return {"api_keys_used": 0, "network_calls_made": 0, "real_exchange_touched": False}
