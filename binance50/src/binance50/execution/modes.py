from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionModeError

from .models import ExecutionMode


def get_execution_mode_policy(mode: ExecutionMode, config: AppConfig) -> dict[str, Any]:
    if mode == ExecutionMode.sandbox:
        mode_conf = config.execution.allowed_modes.sandbox
    elif mode == ExecutionMode.paper_candidate:
        mode_conf = config.execution.allowed_modes.paper_candidate
    elif mode == ExecutionMode.testnet_candidate:
        mode_conf = config.execution.allowed_modes.testnet_candidate
    elif mode == ExecutionMode.live_candidate:
        mode_conf = config.execution.allowed_modes.live_candidate
    else:
        raise ExecutionModeError(f"Unknown mode: {mode}")

    return mode_conf.model_dump()


def validate_mode_enabled(mode: ExecutionMode, config: AppConfig) -> None:
    policy = get_execution_mode_policy(mode, config)
    if not policy.get("enabled", False):
        raise ExecutionModeError(f"Mode {mode} is disabled in configuration")


def assert_mode_can_create_draft(mode: ExecutionMode, config: AppConfig) -> None:
    policy = get_execution_mode_policy(mode, config)
    if not policy.get("can_create_intent_draft", False):
        raise ExecutionModeError(f"Mode {mode} cannot create intent drafts")


def assert_mode_cannot_submit_order(mode: ExecutionMode, config: AppConfig) -> None:
    policy = get_execution_mode_policy(mode, config)
    if policy.get("can_submit_order", False):
        raise ExecutionModeError(f"Mode {mode} allows submitting orders, which is forbidden in Phase 28")


def assert_mode_cannot_call_gateway(mode: ExecutionMode, config: AppConfig) -> None:
    policy = get_execution_mode_policy(mode, config)
    if policy.get("can_call_gateway", False):
        raise ExecutionModeError(f"Mode {mode} allows calling gateway, which is forbidden in Phase 28")


def build_mode_report(config: AppConfig) -> dict[str, Any]:
    return {
        "sandbox": config.execution.allowed_modes.sandbox.model_dump(),
        "paper_candidate": config.execution.allowed_modes.paper_candidate.model_dump(),
        "testnet_candidate": config.execution.allowed_modes.testnet_candidate.model_dump(),
        "live_candidate": config.execution.allowed_modes.live_candidate.model_dump(),
    }
