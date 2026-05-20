import os
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import LiveUnlockError


def get_live_unlock_status(config: AppConfig) -> dict[str, Any]:
    has_unlock = False
    has_risk_ack = False

    expected_unlock = config.safety.live_unlock_phrase_required
    expected_ack = config.safety.live_risk_ack_required

    actual_unlock = os.environ.get("BINANCE50_LIVE_UNLOCK", "")
    actual_ack = os.environ.get("BINANCE50_LIVE_RISK_ACK", "")

    if actual_unlock == expected_unlock:
        has_unlock = True
    if actual_ack == expected_ack:
        has_risk_ack = True

    return {
        "unlock_phrase_present": has_unlock,
        "risk_ack_present": has_risk_ack,
        "requires_manual_unlock": config.safety.require_manual_live_unlock,
        "requires_mainnet_confirmation": config.safety.require_mainnet_confirmation,
    }


def assert_live_unlock_phrase(config: AppConfig) -> None:
    if not config.safety.require_manual_live_unlock:
        return

    expected_unlock = config.safety.live_unlock_phrase_required
    actual_unlock = os.environ.get("BINANCE50_LIVE_UNLOCK", "")

    if actual_unlock != expected_unlock:
        raise LiveUnlockError("Missing or incorrect BINANCE50_LIVE_UNLOCK phrase")


def assert_live_risk_ack(config: AppConfig) -> None:
    if not config.safety.require_mainnet_confirmation:
        return

    expected_ack = config.safety.live_risk_ack_required
    actual_ack = os.environ.get("BINANCE50_LIVE_RISK_ACK", "")

    if actual_ack != expected_ack:
        raise LiveUnlockError("Missing or incorrect BINANCE50_LIVE_RISK_ACK phrase")


def build_live_unlock_report(config: AppConfig) -> dict[str, Any]:
    status = get_live_unlock_status(config)

    blocked = False
    if status["requires_manual_unlock"] and not status["unlock_phrase_present"]:
        blocked = True
    if status["requires_mainnet_confirmation"] and not status["risk_ack_present"]:
        blocked = True

    status["live_blocked_by_unlock_guard"] = blocked
    return status
