from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderStatus
from binance50.core.exceptions import PaperLifecycleError

def transition_paper_order(order: PaperOrder, new_status: PaperOrderStatus, config: AppConfig) -> PaperOrder:
    validate_paper_lifecycle_transition(order.status, new_status, config)
    order.status = new_status
    return order

def validate_paper_lifecycle_transition(old_status: PaperOrderStatus, new_status: PaperOrderStatus, config: AppConfig) -> None:
    reject_exchange_lifecycle_state(new_status.value, config)

    valid_transitions = {
        PaperOrderStatus.paper_draft: [PaperOrderStatus.paper_submitted_local],
        PaperOrderStatus.paper_submitted_local: [PaperOrderStatus.paper_accepted_local],
        PaperOrderStatus.paper_accepted_local: [
            PaperOrderStatus.paper_partially_filled_local,
            PaperOrderStatus.paper_filled_local,
            PaperOrderStatus.paper_rejected_local,
            PaperOrderStatus.paper_expired_local
        ],
        PaperOrderStatus.paper_partially_filled_local: [
            PaperOrderStatus.paper_filled_local,
            PaperOrderStatus.paper_expired_local
        ],
        PaperOrderStatus.paper_filled_local: [PaperOrderStatus.paper_archived],
        PaperOrderStatus.paper_rejected_local: [PaperOrderStatus.paper_archived],
        PaperOrderStatus.paper_expired_local: [PaperOrderStatus.paper_archived],
        PaperOrderStatus.paper_canceled_local: [PaperOrderStatus.paper_archived],
    }

    if new_status == PaperOrderStatus.paper_canceled_local:
        if old_status in [PaperOrderStatus.paper_filled_local, PaperOrderStatus.paper_rejected_local, PaperOrderStatus.paper_expired_local, PaperOrderStatus.paper_archived]:
            raise PaperLifecycleError(f"Cannot cancel a terminal order: {old_status}")
    elif new_status not in valid_transitions.get(old_status, []):
        raise PaperLifecycleError(f"Invalid transition from {old_status} to {new_status}")

def reject_exchange_lifecycle_state(state: str, config: AppConfig) -> None:
    if config.paper_execution.lifecycle.exchange_state_forbidden and state in config.paper_execution.lifecycle.forbidden_states:
        raise PaperLifecycleError(f"Exchange state {state} is forbidden in paper mode")

def build_paper_lifecycle_report(orders: list[PaperOrder]) -> dict:
    return {"total": len(orders), "status_counts": {status.value: sum(1 for o in orders if o.status == status) for status in PaperOrderStatus}}
