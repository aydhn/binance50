import uuid
from typing import Any
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder
from binance50.core.exceptions import PaperOrderError

def create_paper_order(**kwargs: Any) -> PaperOrder:
    return PaperOrder(**kwargs)

def validate_paper_order_fields(order: PaperOrder, config: AppConfig) -> None:
    if not order.paper_order_id.startswith(config.paper_execution.order.internal_order_id_prefix):
        raise PaperOrderError(f"Paper order ID must start with {config.paper_execution.order.internal_order_id_prefix}")
    assert_no_exchange_order_identifiers(order)
    assert_order_local_only(order)

def generate_paper_order_id(config: AppConfig) -> str:
    return f"{config.paper_execution.order.internal_order_id_prefix}{uuid.uuid4().hex[:12]}"

def order_to_redacted_dict(order: PaperOrder) -> dict[str, Any]:
    return order.dict(exclude={"metadata"})

def assert_no_exchange_order_identifiers(order: PaperOrder) -> None:
    if "exchange_order_id" in order.metadata or "client_order_id" in order.metadata:
        raise PaperOrderError("Exchange order identifiers are strictly forbidden in paper orders")

def assert_order_local_only(order: PaperOrder) -> None:
    if "network_submitted" in order.metadata:
        raise PaperOrderError("Order must be local only")
