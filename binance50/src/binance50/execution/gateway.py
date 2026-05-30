from typing import Any, Protocol

from .models import ExecutionIntentDraft


class ExecutionGateway(Protocol):
    def name(self) -> str:
        ...

    def mode(self) -> str:
        ...

    def is_enabled(self) -> bool:
        ...

    def submit_intent(self, intent: ExecutionIntentDraft) -> dict[str, Any]:
        ...

    def cancel_intent(self, intent_id: str) -> dict[str, Any]:
        ...

    def health(self) -> dict[str, Any]:
        ...

    def safety_report(self) -> dict[str, Any]:
        ...
