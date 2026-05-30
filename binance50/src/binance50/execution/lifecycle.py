from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionLifecycleError

from .models import ExecutionIntentDraft, ExecutionIntentStatus


def validate_lifecycle_transition(old_status: str, new_status: str, config: AppConfig) -> None:
    allowed = config.execution.lifecycle.allowed_states
    forbidden = config.execution.lifecycle.forbidden_states

    if new_status in forbidden:
        raise ExecutionLifecycleError(f"Status '{new_status}' is forbidden in Phase 28.")

    if new_status not in allowed:
        raise ExecutionLifecycleError(f"Status '{new_status}' is not an allowed internal status.")


def transition_intent_status(intent: ExecutionIntentDraft, new_status: ExecutionIntentStatus, config: AppConfig) -> ExecutionIntentDraft:
    validate_lifecycle_transition(intent.status, new_status.value, config)
    intent.status = new_status
    return intent


def reject_exchange_lifecycle_state(state: str, config: AppConfig) -> None:
    if config.execution.lifecycle.exchange_state_forbidden:
        forbidden = config.execution.lifecycle.forbidden_states
        if state in forbidden:
            raise ExecutionLifecycleError(f"Exchange state '{state}' is strictly forbidden.")


def build_lifecycle_report(intents: list[ExecutionIntentDraft]) -> dict[str, Any]:
    counts = {}
    for i in intents:
        counts[i.status.value] = counts.get(i.status.value, 0) + 1
    return {
        "intent_count": len(intents),
        "status_distribution": counts
    }
