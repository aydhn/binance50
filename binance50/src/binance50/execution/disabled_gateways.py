from typing import Any

from binance50.core.exceptions import ExecutionGatewayDisabledError

from .gateway import ExecutionGateway
from .models import ExecutionIntentDraft


class DisabledPaperGateway(ExecutionGateway):
    def name(self) -> str:
        return "DisabledPaperGateway"

    def mode(self) -> str:
        return "paper_candidate"

    def is_enabled(self) -> bool:
        return False

    def submit_intent(self, intent: ExecutionIntentDraft) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Paper gateway is disabled in Phase 28.")

    def cancel_intent(self, intent_id: str) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Paper gateway is disabled in Phase 28.")

    def health(self) -> dict[str, Any]:
        return {"status": "disabled", "reason": "Phase 28 hard limit"}

    def safety_report(self) -> dict[str, Any]:
        return {"network_calls": 0, "api_keys_used": False, "mode": "paper_candidate"}


class DisabledTestnetGateway(ExecutionGateway):
    def name(self) -> str:
        return "DisabledTestnetGateway"

    def mode(self) -> str:
        return "testnet_candidate"

    def is_enabled(self) -> bool:
        return False

    def submit_intent(self, intent: ExecutionIntentDraft) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Testnet gateway is disabled in Phase 28.")

    def cancel_intent(self, intent_id: str) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Testnet gateway is disabled in Phase 28.")

    def health(self) -> dict[str, Any]:
        return {"status": "disabled", "reason": "Phase 28 hard limit"}

    def safety_report(self) -> dict[str, Any]:
        return {"network_calls": 0, "api_keys_used": False, "mode": "testnet_candidate"}


class DisabledLiveGateway(ExecutionGateway):
    def name(self) -> str:
        return "DisabledLiveGateway"

    def mode(self) -> str:
        return "live_candidate"

    def is_enabled(self) -> bool:
        return False

    def submit_intent(self, intent: ExecutionIntentDraft) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Live gateway is disabled in Phase 28.")

    def cancel_intent(self, intent_id: str) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Live gateway is disabled in Phase 28.")

    def health(self) -> dict[str, Any]:
        return {"status": "disabled", "reason": "Phase 28 hard limit"}

    def safety_report(self) -> dict[str, Any]:
        return {"network_calls": 0, "api_keys_used": False, "mode": "live_candidate"}


class DisabledTestOrderGateway(ExecutionGateway):
    def name(self) -> str:
        return "DisabledTestOrderGateway"

    def mode(self) -> str:
        return "live_candidate" # the /test endpoint goes to live but doesn't place

    def is_enabled(self) -> bool:
        return False

    def submit_intent(self, intent: ExecutionIntentDraft) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Test order gateway (/api/v3/order/test) is disabled in Phase 28.")

    def cancel_intent(self, intent_id: str) -> dict[str, Any]:
        raise ExecutionGatewayDisabledError("Test order gateway (/api/v3/order/test) is disabled in Phase 28.")

    def health(self) -> dict[str, Any]:
        return {"status": "disabled", "reason": "Phase 28 hard limit"}

    def safety_report(self) -> dict[str, Any]:
        return {"network_calls": 0, "api_keys_used": False, "mode": "live_test_endpoint"}
